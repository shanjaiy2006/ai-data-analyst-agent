from app.services.analyst_service import analyze_question


question = "Find unusual transaction amounts"


result = analyze_question(question)


print("\n")
print("=" * 60)
print("AI DATA ANALYST")
print("=" * 60)

print("\nQuestion:")
print(result["question"])


if result["success"]:

    print("\nAI PLAN:")
    print(result["plan"])

    print("\nGenerated SQL:")
    print(result["sql"])

    print("\nRaw Results:")
    print("-" * 60)

    for row in result["results"]:
        print(row)

    if result["data_analysis"]:

        print("\nDATA ANALYSIS:")
        print("-" * 60)

        data_analysis = result["data_analysis"]

        print("Rows:", data_analysis["row_count"])
        print("Columns:", data_analysis["column_count"])

        print("\nNumeric Summary:")

        for column, values in data_analysis["numeric_summary"].items():
            print(column, ":", values)

    if result["anomalies"]:

        print("\nANOMALIES:")
        print("-" * 60)

        anomalies = result["anomalies"]

        print(
            "Anomalies Found:",
            anomalies["anomalies_found"]
        )

        print(
            "Total Anomalies:",
            anomalies["total_anomalies"]
        )

        for item in anomalies["details"]:

            print(
                f"\nColumn: {item['column']}"
            )

            print(
                f"Value: {item['value']}"
            )

            print(
                f"Row: {item['row']}"
            )

    if result["chart"]:

        print("\nCHART:")
        print("-" * 60)
        print(result["chart"])

    print("\nAI INSIGHT:")
    print("-" * 60)

    print(result["analysis"])

else:

    print("\nERROR:")
    print(result["error"])