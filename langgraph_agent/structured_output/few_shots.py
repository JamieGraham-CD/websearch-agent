# ---------------------------------------------------------------
# FEW-SHOT EXAMPLES – one or two valid instances for every model
# ---------------------------------------------------------------
few_shot_examples = {
    "Agreement Type": """[
        {"value": "PILOT", "explanation": "This is a pilot agreement as specified in the filepath name, and in the first page of the document.", "source_pdf_path": "Abunsh pilot agreement.txt"},
        {"value": "MASTER AGREEMENT", "explanation": "This is a master service agreement as specified in Section 1 of the document.", "source_pdf_path": "Onto Master Services Agreement.txt"},
        {"value": "SOW", "explanation": "This is a statement of work as specified in the first page of the document.", "source_pdf_path": "JDFH SOW.txt"}
        {"value": "AMENDMENT", "explanation": "This is an amendment to the existing master agreement.", "source_pdf_path": "Onto Master Services Agreement-amendment.txt"}
    ]""",

    "Background Checks": """[
        {"value": "Yes", "explanation": "§ 5.4 requires background checks for all on-site staff", "source_pdf_path": "psa_bg_checks.txt"},
        {"value": "No", "explanation": "No mention of background checks in the document", "source_pdf_path": "saas_terms.txt"},
        {"value": "Removed", "explanation": "There is specific language stating that background checks have been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]""",

    "Biometric Language": """[
        {"value": "Yes", "explanation": "Appendix B covers fingerprint template storage", "source_pdf_path": "timeclock_addendum.txt"},
        {"value": "No", "explanation": "No mention of biometric language is in the document", "source_pdf_path": "timeclock_addendum2.txt"}
        {"value": "Removed", "explanation": "There is specific language stating that biometric language has been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]""",

    "BAA": """[
        {"value": "Yes", "explanation": "HIPAA Business Associate Agreement attached as Exhibit C", "source_pdf_path": "healthcare_msa.txt"},
        {"value": "No", "explanation": "There is no mention of a Business Associate Agreement in the document", "source_pdf_path": "general_services_agreement.txt"}
        {"value": "Removed", "explanation": "There is specific language stating that the BAA has been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]""",

    "Business Downturn Consequences": """[
        {"value": "Yes", "explanation": "The document shows clear provisions for business downturn consequences in section C..", "source_pdf_path": "vendor_paper_schedule_z.txt"},
        {"value": "No", "explanation": "There is no text related to business downturn consequences in the provided document.", "source_pdf_path": "vendor_paper_schedule_z.txt"},
        {"value": "Removed", "explanation": "There is specific language stating that provisions related to business downturn consequences have been removed from the contract.", "source_pdf_path": "vendor_paper_schedule_z.txt"}
    ]""",

    "Canadian Addendum": """[
        {"value": "No", "explanation": "There is no mention of a Canadian Addendum or section in the document", "source_pdf_path": "us_only_msa.txt"},
        {"value": "Yes", "explanation": "Canada-specific addendum or section included as Exhibit E", "source_pdf_path": "canada_addendum.txt"}
        {"value": "Removed", "explanation": "There is specific language stating that the Canadian Addendum/section has been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]
    - This field is looking for whether Compass is able to do business with the vendor in Canada.
    - When searching for the Canadian Addendum/section via hybrid search tool, try looking for the following keywords as well as the ones you come up with:
    "canada", "canadian", "addendum", "section".
    - If the contract mentions a Canada-specific addendum or section in the contract, return "Yes", otherwise return "No".
    """,

    "Client Termination For Convenience Notice Period Days": """[
        {"value": "30", "explanation": "§ 12(b) grants 30-day termination-for-convenience right", "source_pdf_path": "msa_section12.txt"},
        {"value": "No", "explanation": "Contract silent on T-for-C", "source_pdf_path": "hardware_supply_agreement.txt"}
        {"value": "No", "explanation": "The contract mentions a notice period for credit memo or some other purpose, not for client termination for convenience.", "source_pdf_path": "ambiguous_clause.txt"}
    ]
    - IMPORTANT: Do not infer the notice period for a different period, such as credit memo, etc. In your retrieved context, the notice period itself has to specifically be about termination of the contract.
    - Termination notice period absolutely needs to be mentioned in the retrieved context, otherwise return "No".
    - If the contract does not specify a notice period specifically for termination of the contract, return "No".
    - If the contract specifies a notice period, but it doesn't specifically say it's about termination of the contract, return "No".
    """,

    "Vendor Name": """[
        {"value": "ACME Technologies", "explanation": "Exact legal name on title page", "source_pdf_path": "acme_signed_msa.txt"},
        {"value": "Global Widgets", "explanation": "Taken from signature block", "source_pdf_path": "widgets_po_terms.txt"}
        {"value": "Agilysys", "explanation": "Taken from signature block", "source_pdf_path": "widgets_po_terms.txt"}
    ]
    - Note that suffixes like Inc, LLC, etc should be avoided in the extracted value. Take only the core vendor name as it appears in the document. e.g. "Agilysys" not "Agilysis NV LLC.".
    """,

    "DPA": """[
        {"value": "Yes", "explanation": "Data Processing Addendum attached and signed", "source_pdf_path": "dpa_exhibit.txt"},
        {"value": "No", "explanation": "There is no mention of a Data Processing Addendum in the document", "source_pdf_path": "legacy_contract_2018.txt"}
        {"value": "Removed", "explanation": "There is specific language stating that the DPA has been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]
    - When searching for the DPA via hybrid search tool, try looking for the following keywords as well as the ones you come up with:
    "data processing", "data privacy", "addendum", "dpa". 
    - If the contract mentions a Data Processing or Data Privacy Addendum/Agreement/Section in the contract, return "Yes", otherwise return "No".
    - It does not have to be a full addendum/agreement, it can simply be a section of the document detailing data privacy/processing, or it can be a separate addendum/agreement that is attached and signed.
    """,

    "Effective Date": """[
        {"value": "03-15-2025", "explanation": "Defined in preamble", "source_pdf_path": "signed_msa.txt"},
        {"value": "07-01-2024", "explanation": "Not defined; used earliest signature date", "source_pdf_path": "counter_signed_order_form.txt"},
        {"value": "", "explanation": "No effective date clause found", "source_pdf_path": "legacy_agreement.txt"}
    ]
    - Note that while this date may be in a variety of formats in the text, you should return a date in the format MM-DD-YYYY as given above for the values.
    """,

    "Non-Renewal Notice": """[
        {"value": 90, "explanation": "Auto-renew clause requires 90-day non-renewal notice", "source_pdf_path": "evergreen_terms.txt"},
        {"value": No, "explanation": "Agreement is fixed 24-month term, no auto-renew", "source_pdf_path": "fixed_term_contract.txt"}
    ]
    - This field is the advance notice (days) required to prevent an automatic renewal.
    - For this field, the notice period you extract needs to specifically prevent an automatic renewal! 
    - When searching for the non-renewal notice via hybrid search tool, try looking for the following keywords as well as the ones you come up with:
    "renew", "non-renew", "notice", "auto".
    """,

    "Initial Term Expiration": """[
        {"value": "06-30-2026", "explanation": "Two-year term ends 30 Jun 2026", "source_pdf_path": "term_sheet.txt"},
        {"value": "01-01-2027", "explanation": "The contract's effective date is 1 Jan 2026 and has initial term duration of 1 year, ends on 1 Jan 2027", "source_pdf_path": "start_term.txt"},
        {"value": "01-08-2027", "explanation": "The contract is last signed on 8 Jan 2026 and has initial term duration of 1 year, ends on 8 Jan 2027", "source_pdf_path": ".txt"},
        {"value": "N/A", "explanation": "Perpetual licence until terminated", "source_pdf_path": "perpetual_license.txt"}
    ]
    - If the text mentions the expiration date of the initial term, extract the date and return your answer in the format MM-DD-YYYY.
    - If no end date is specified, but the initial term duration is known and any of the following dates are specified:
        1. effective date, 2. last signature date, 3. start date
        then calculate the end date based on that information.
    """,

    "Paper Type": """[
        {"value": "Vendor", "explanation": "Contract drafted on vendor paper", "source_pdf_path": "vendor_master_terms.txt"},
        {"value": "Vendor & Schedule Z", "explanation": "Contract includes both vendor paper and a Schedule Z which is a compass template.", "source_pdf_path": "vendor_master_terms.txt"},
        {"value": "Compass", "explanation": "Compass standard template used", "source_pdf_path": "compass_template_msa.txt"}
    ]
    
     This field describes the business entity that drafted the contract, is it on Compass paper vs Vendor paper vs Vendor & Schedule Z.
        - Compass: The contract is drafted on Compass paper, meaning it is a standard contract template used by Compass.
        - Vendor: The contract is drafted on Vendor paper, meaning it is a contract template used by the vendor.
        - Vendor & Schedule Z: The contract is drafted on Vendor paper, but it includes a Schedule Z, which is an additional Compass template that may contain specific terms or conditions related to the contract.
        Guidelines:
        - If the contract is drafted on Compass paper, return "Compass".
        - If the contract is drafted is not obviously drafted on Compass paper and could plausibly be on Vendor paper, return "Vendor".
        - If the contract is drafted on Vendor & Schedule Z paper, return "Vendor & Schedule Z".
    """,

    "Payment Terms": """[
        {"value": "Net 60", "explanation": "Section 1.5 in the document that specifies payment terms as '60 days from invoice'.", "source_pdf_path": "billing_terms.txt"},
        {"value": "Net 30", "explanation": "Section 10 in the document that specifies payment terms as '30 days from invoice'.", "source_pdf_path": "po.txt"},
        {"value": "No", "explanation": "The contract mentions a term duration for a credit memo/an other purpose, not for the payment terms from the invoice.", "source_pdf_path": "ambiguous_clause.txt"}
    ]
    This field should return one of the following normalized values:
    - "Net <days>": where <days> is an integer, representing the number of days within which payment is due specifically from the invoice date. For example, "Net 30" means payment is due within 30 days from the invoice date.
    - "No": if there are no such payment terms specified in the contract.
    """,

    "Price Increase Mechanism": """[
        {"value": "CPI", "explanation": "Adjustments are referenced based on the Consumer Price Index (CPI).", "source_pdf_path": "pricing_schedule.txt"},
        {"value": "3-5%", "explanation": "Agreement specifies a 3-5% annual price increase.", "source_pdf_path": "fixed_price_addendum.txt"}
        {"value": "No", "explanation": "There is no mention of a price increase mechanism in the document", "source_pdf_path": "saas_terms.txt"}
        {"value": "Other", "explanation": "There is a price increase mechanism that is not one of the other options", "source_pdf_path": "saas_terms.txt"}
    ]
    Additional Notes about CPI vs CPI-W: 
    - CPI (Consumer Price Index)
        - Measures the average change over time in the prices paid by all urban consumers for a basket of goods and services.
        - Represents about 93% of the total U.S. population.
        - Also referred to as CPI-U (Consumer Price Index for All Urban Consumers).
    - CPI-W (Consumer Price Index for Urban Wage Earners and Clerical Workers)
        - Measures the same set of goods and services as CPI, but focuses specifically on urban households that derive more than 50% of their income from clerical or wage occupations.
    - Keywords to include in hybrid search can include: "price", "increase", "adjustment", "cpi", "consumer price index", "price increase", "mechanism". 
    """,

    "Quality Assurance": """[
        {"value": "Yes", "explanation": "Section 9 includes QA standards for food safety", "source_pdf_path": "kitchen_services_agreement.txt"},
        {"value": "No", "explanation": "There is no mention of Quality Assurance in the document", "source_pdf_path": "saas_agreement.txt"}
        {"value": "Removed", "explanation": "There is specific language stating that Quality Assurance has been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]""",

    "Renewal Term": """[
        {"value": "1 year", "explanation": "Auto-renews for successive 12-month terms", "source_pdf_path": "renewal_clause.txt"},
        {"value": "3 years", "explanation": "Mutual renewal for additional three-year periods", "source_pdf_path": "long_term_facilities_contract.txt"}
    ]""",

    "Service Credits": """[
        {"value": "Yes", "explanation": "Schedule 2 defines credit formula for SLA breaches", "source_pdf_path": "sla_schedule.txt"},
        {"value": "No", "explanation": "There is no mention of service credits in the document", "source_pdf_path": "consulting_sow.txt"},
        {"value": "Removed", "explanation": "There is specific language stating that service credits have been removed from the contract.", "source_pdf_path": "saas_terms.txt"},
        {"value": "No", "explanation": "The contract mentions credit memos but does not define any service-credit remedies.", "source_pdf_path": "credit_memo_clause.txt"}
    ]""",

    "Term Type": """[
        {"value": "Fixed Term", "explanation": "12-month fixed term stated in § 3", "source_pdf_path": "one_year_msa.txt"},
        {"value": "Automatic Renewal In Perpetuity (Evergreen)", "explanation": "Renews indefinitely until either party gives notice", "source_pdf_path": "evergreen_license.txt"},
        {"value": "Other", "explanation": "No term clause found", "source_pdf_path": "legacy_nodate_contract.txt"}
    ]
    When searching for the term type, try looking for the following keywords as well as the ones you come up with:
    - "fixed term"
    - "perpetual"
    - "renewal"
    - "automatic"
    - "auto"
    """,

    "Biometrics": """[
        {"value": "No", "explanation": "No biometric data processed", "source_pdf_path": "privacy_scope.txt"},
        {"value": "Yes", "explanation": "Time-clock system stores fingerprint hash", "source_pdf_path": "biometric_addendum.txt"}
        {"value": "Removed", "explanation": "There is specific language stating that biometric data has been removed from the contract.", "source_pdf_path": "saas_terms.txt"}
    ]""",

    "Data Source": """[
        {"value": ["Employee", "Client"], "explanation": "System stores HR and client data", "source_pdf_path": "dpa_scope.txt"},
        {"value": ["Consumer"], "explanation": "E-commerce platform processes consumer orders", "source_pdf_path": "privacy_policy.txt"}
    ]
    - Think step by step to determine whether the contract language specifies data sources. If it doesn't, return empty list. This field is meant to capture the types of data sources that the system interacts with. It can be a list of multiple values, such as ["Compass", "Client"] or ["Consumer"]. 
    """,

    "Invoice Frequency": """[
        {"value": "Monthly", "explanation": "Section 4.2 states invoices are issued monthly for services rendered.", "source_pdf_path": "monthly_billing_clause.txt"},
        {"value": "Quarterly", "explanation": "The agreement specifies that invoices are to be sent every three months.", "source_pdf_path": "quarterly_invoice_terms.txt"},
        {"value": "Annually", "explanation": "Section 7.1: Vendor will invoice Compass annually in advance.", "source_pdf_path": "annual_invoice_clause.txt"},
        {"value": "No", "explanation": "The contract does not specify an invoice frequency.", "source_pdf_path": "no_invoice_frequency.txt"},
        {"value": "No", "explanation": "The only frequency numbers mentioned are for [other purpose], not invoice frequency.", "source_pdf_path": "ambiguous_case.txt"}
    ]
    - Try to use concise standard terms to describe the frequency: "Weekly", "Biweekly", "Monthly", "Quarterly", "Annually", etc.
    - If the frequency is not a standard term, return a concise description: "Every <days> days" where <days> is an integer (e.g. "Every 45 days").
    - If no frequency is specified, return "No".
    """,

    "Fully Executed with Dual Signatures": """[
        {
            "value": "Yes",
            "explanation": "Both signature blocks on the last page are completed by authorized representatives of each party.",
            "source_pdf_path": "master_service_agreement.pdf"
        },
        {
            "value": "No",
            "explanation": "Only the vendor’s signature appears; the counterparty’s signature block is blank.",
            "source_pdf_path": "nda_unsigned_counterparty.pdf"
        }
        - Note: Use "signature" as one of your keywords here.
    ]""",

    "Counterparty Signature": """[
        {
            "value": "Yes",
            "explanation": "Counterparty signed and dated the signature block on page 2.",
            "source_pdf_path": "vendor_contract.pdf"
        },
        {
            "value": "No",
            "explanation": "No signature or date found in the counterparty’s signature section.",
            "source_pdf_path": "supply_agreement.pdf"
        }
        - Note: Use "signature" as one of your keywords here.
    ]""",

    "Countersigned": """[
        {
            "value": "Yes",
            "explanation": "Document bears a countersignature by the second party on page 3.",
            "source_pdf_path": "employment_agreement.pdf"
        },
        {
            "value": "No",
            "explanation": "Countersignature block is present but remains unsigned.",
            "source_pdf_path": "consulting_agreement.pdf"
        }
        - Note: Use "signature" as one of your keywords here.
    ]""",

    "Highly Sensitive PII": """[
        {"value": "No", "explanation": "Only work email addresses collected", "source_pdf_path": "data_classification.txt"},
        {"value": "Yes", "explanation": "Stores passport numbers of employees", "source_pdf_path": "hr_module_spec.txt"}
    ]""",

    "PCI": """[
        {"value": "Yes", "explanation": "Handles credit-card transactions (card-present)", "source_pdf_path": "pci_appendix.txt"},
        {"value": "No", "explanation": "Payment processing handled by third-party; no PCI data stored", "source_pdf_path": "outsourcing_agreement.txt"}
    ]""",

    "PHI": """[
        {"value": "No", "explanation": "System not used for healthcare data", "source_pdf_path": "scope_of_services.txt"},
        {"value": "Yes", "explanation": "EHR integration stores patient records", "source_pdf_path": "hipaa_addendum.txt"}
    ]""",

    "Sensitive PII": """[
        {"value": "Yes", "explanation": "Collects DOB and home address of clients", "source_pdf_path": "client_intake_form.txt"},
        {"value": "No", "explanation": "Only aggregates anonymised metrics", "source_pdf_path": "analytics_module_desc.txt"}
    ]""",

    "Agreement Risk Notes": """[
        {"value": "Overall LOW risk – liability capped and no vendor-favoured indemnities.", "explanation": "Legal counsel assessment 2025-04-03", "source_pdf_path": "risk_summary.txt"},
        {"value": "Medium risk due to unlimited liability for data breach.", "explanation": "Flagged by security team", "source_pdf_path": "legal_review_memo.txt"}
    ]""",

    "Market Stability Risk Score": """[
        {"value": "LOW", "explanation": "Vendor is profitable public company", "source_pdf_path": "dnb_report.txt"},
        {"value": "HIGH", "explanation": "Start-up with negative cash flow and no funding round closed", "source_pdf_path": "vendor_financials.txt"}
    ]""",

    "Market Stability Risk Notes": """[
        {"value": "Audited 10-K shows consistent revenue growth.", "explanation": "Source: SEC filings", "source_pdf_path": "10k_2024.txt"},
        {"value": "Balance sheet indicates < 6 months runway.", "explanation": "Source: unaudited statements", "source_pdf_path": "startup_financials.xlsx"}
    ]""",

    "Stakeholder Performance Risk Score": """[
        {"value": "MEDIUM", "explanation": "Two SLA misses last quarter", "source_pdf_path": "sla_report_q1.txt"},
        {"value": "LOW", "explanation": "Meets all SLAs for past 12 months", "source_pdf_path": "sla_dashboard.txt"}
    ]""",

    "Stakeholder Performance Risk Notes": """[
        {"value": "Latency SLA breached in Jan & Feb, vendor issued credits.", "explanation": "Tickets 4521 & 4533", "source_pdf_path": "ticket_log.xlsx"},
        {"value": "Customer satisfaction score 95 %.", "explanation": "Quarterly vendor review", "source_pdf_path": "qbr_slide_deck.txt"}
    ]""",

    "VSO Agreement Risk Score": """[
        {"value": "LOW", "explanation": "No material exceptions; DP terms strong", "source_pdf_path": "risk_matrix.txt"},
        {"value": "HIGH", "explanation": "Unlimited liability + weak security controls", "source_pdf_path": "exception_summary.txt"}
    ]""",

    "VSO Risk Score": """[
        {"value": "LOW", "explanation": "Composite score LOW across all factors", "source_pdf_path": null},
        {"value": "MEDIUM", "explanation": "Elevated due to performance history", "source_pdf_path": "combined_risk_report.txt"}
    ]""",

    "VSO Risk Score Notes": """[
        {"value": "See individual risk factors; overall profile acceptable.", "explanation": "Prepared by procurement", "source_pdf_path": "risk_overview.xlsx"},
        {"value": "Monitor financial stability; recommend quarterly review.", "explanation": "Finance team note", "source_pdf_path": "finance_memo.txt"}
    ]"""
}