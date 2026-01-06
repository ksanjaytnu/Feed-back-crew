from .crew import OrganizationFeedbackCrew


def run():
    print("=== Organization Feedback Intelligence Crew ===\n")

    company_name = input("Enter your company name: ").strip()

    if not company_name:
        print("❌ Company name cannot be empty.")
        return

    print(f"\n🔍 Analyzing feedback for company: {company_name}\n")

    crew_instance = OrganizationFeedbackCrew()

    result = crew_instance.crew().kickoff(
        inputs={
            "company_name": company_name  # 🔥 must match YAML exactly
        }
    )

    print("\n=== FINAL ORGANIZATION FEEDBACK REPORT ===\n")
    print(result)


if __name__ == "__main__":
    run()
