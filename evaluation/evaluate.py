"""
SWYNEX Final AI Application - System Evaluation & Benchmark Script
Runs empirical evaluation across curated test cases in data/evaluation_cases.json,
computes scikit-learn classification metrics (Accuracy, Precision, Recall, F1),
evaluates priority and deadline detection, and exports results to evaluation_results.csv.
HONEST EVALUATION: Metrics are calculated directly from empirical predictions.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import analyze_announcement, CATEGORIES


def load_evaluation_cases() -> List[Dict[str, Any]]:
    cases_path = PROJECT_ROOT / "data" / "evaluation_cases.json"
    if not cases_path.exists():
        raise FileNotFoundError(f"Evaluation cases not found at {cases_path}")
    with open(cases_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_evaluation() -> Dict[str, Any]:
    """
    Executes benchmark evaluation across all test cases.
    Returns calculated metrics, classification reports, and case-by-case dataframe.
    """
    test_cases = load_evaluation_cases()

    records: List[Dict[str, Any]] = []
    y_true_cat: List[str] = []
    y_pred_cat: List[str] = []
    y_true_prio: List[str] = []
    y_pred_prio: List[str] = []
    y_true_dl: List[bool] = []
    y_pred_dl: List[bool] = []

    for item in test_cases:
        case_id = item["id"]
        desc = item["description"]
        text = item["text"]
        exp_cat = item["expected_category"]
        exp_prio = item["expected_priority"]
        exp_dl = item["has_deadline"]
        is_edge = item.get("is_edge_case", False)
        inp_type = item.get("input_type", "standard")

        result = analyze_announcement(text)

        pred_cat = result["classification"]["category"]
        conf = result["classification"]["confidence"]
        pred_prio = result["priority"]["priority"]
        prio_score = result["priority"]["score"]
        pred_dl = result["extraction"]["has_deadline"]
        dates_found = ", ".join(result["extraction"]["dates"]) if result["extraction"]["dates"] else "None"
        deadlines_found = ", ".join(result["extraction"]["deadlines"]) if result["extraction"]["deadlines"] else "None"
        summary_txt = result["summary"]["summary"]

        cat_match = (pred_cat == exp_cat)
        prio_match = (pred_prio == exp_prio)
        dl_match = (pred_dl == exp_dl)

        y_true_cat.append(exp_cat)
        y_pred_cat.append(pred_cat)
        y_true_prio.append(exp_prio)
        y_pred_prio.append(pred_prio)
        y_true_dl.append(exp_dl)
        y_pred_dl.append(pred_dl)

        records.append({
            "id": case_id,
            "description": desc,
            "input_type": inp_type,
            "is_edge_case": is_edge,
            "expected_category": exp_cat,
            "predicted_category": pred_cat,
            "category_match": cat_match,
            "confidence": conf,
            "expected_priority": exp_prio,
            "predicted_priority": pred_prio,
            "priority_match": prio_match,
            "priority_score": prio_score,
            "expected_deadline": exp_dl,
            "detected_deadline": pred_dl,
            "deadline_match": dl_match,
            "extracted_dates": dates_found,
            "extracted_deadlines": deadlines_found,
            "summary_snippet": summary_txt[:80] + ("..." if len(summary_txt) > 80 else ""),
        })

    df_results = pd.DataFrame(records)

    # Scikit-Learn Metric Computations
    cat_accuracy = float(accuracy_score(y_true_cat, y_pred_cat))
    prio_accuracy = float(accuracy_score(y_true_prio, y_pred_prio))
    dl_accuracy = float(accuracy_score(y_true_dl, y_pred_dl))

    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true_cat, y_pred_cat, average="weighted", zero_division=0
    )
    macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(
        y_true_cat, y_pred_cat, average="macro", zero_division=0
    )

    clf_report = classification_report(
        y_true_cat, y_pred_cat, output_dict=True, zero_division=0
    )

    # Standard vs Edge case breakdown
    std_mask = ~df_results["is_edge_case"]
    std_cat_acc = float(accuracy_score(
        [y_true_cat[i] for i, m in enumerate(std_mask) if m],
        [y_pred_cat[i] for i, m in enumerate(std_mask) if m]
    )) if any(std_mask) else 0.0

    edge_mask = df_results["is_edge_case"]
    edge_cat_acc = float(accuracy_score(
        [y_true_cat[i] for i, m in enumerate(edge_mask) if m],
        [y_pred_cat[i] for i, m in enumerate(edge_mask) if m]
    )) if any(edge_mask) else 0.0

    # Save to CSV
    csv_path = PROJECT_ROOT / "evaluation" / "evaluation_results.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(csv_path, index=False)

    return {
        "total_test_cases": len(test_cases),
        "standard_cases_count": int(sum(std_mask)),
        "edge_cases_count": int(sum(edge_mask)),
        "category_accuracy": round(cat_accuracy * 100, 2),
        "standard_category_accuracy": round(std_cat_acc * 100, 2),
        "edge_case_accuracy": round(edge_cat_acc * 100, 2),
        "priority_accuracy": round(prio_accuracy * 100, 2),
        "deadline_accuracy": round(dl_accuracy * 100, 2),
        "weighted_precision": round(float(prec) * 100, 2),
        "weighted_recall": round(float(rec) * 100, 2),
        "weighted_f1": round(float(f1) * 100, 2),
        "macro_f1": round(float(macro_f1) * 100, 2),
        "classification_report": clf_report,
        "results_dataframe": df_results,
        "csv_path": str(csv_path),
    }


if __name__ == "__main__":
    print("=================================================================")
    print(" SWYNEX Final AI Application - Empirical Evaluation Benchmark")
    print("=================================================================")
    eval_summary = run_evaluation()
    print(f"\nTotal Test Cases Evaluated : {eval_summary['total_test_cases']}")
    print(f"Standard Announcement Cases : {eval_summary['standard_cases_count']}")
    print(f"Edge & Failure Test Cases   : {eval_summary['edge_cases_count']}")
    print("-----------------------------------------------------------------")
    print(f"Category Overall Accuracy   : {eval_summary['category_accuracy']}%")
    print(f"Standard Cases Accuracy     : {eval_summary['standard_category_accuracy']}%")
    print(f"Edge Cases Accuracy         : {eval_summary['edge_case_accuracy']}%")
    print(f"Priority Scoring Accuracy   : {eval_summary['priority_accuracy']}%")
    print(f"Deadline Detection Accuracy : {eval_summary['deadline_accuracy']}%")
    print(f"Weighted Macro F1-Score     : {eval_summary['weighted_f1']}%")
    print("-----------------------------------------------------------------")
    print(f"Results exported to: {eval_summary['csv_path']}")
    print("=================================================================")
