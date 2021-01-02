class AnalysisHandler:
    def handle(self):
        
        body = []

        if "all" in params.get("actions"):
            body = full_analysis().to_json(orient="records")

        elif len(params.get("actions")) == 1:
            if "find-max-profit" in params.get("actions"):
                body = find_max_profit().to_json(orient="records")
            elif "indicator-combinations" in params.get("actions"):
                body = indicator_combinations().to_json(orient="records")
            elif "track-trends" in params.get("actions"):
                body = track_trends().to_json(orient="records")

            else:
                body = combination_analysis().to_json(orient="records")

        if body:
            return 200, body

        return 501, json.dumps("Something went wrong while processing the request.")

    def full_analysis(self):
            # run a combination of all three functions here
        print("filler")

    def combination_analysis(self):
            # run a combination of provided functions here
        print("filler")