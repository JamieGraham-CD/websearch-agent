from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal, Annotated, List
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
import datetime as dt
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# Shared config mix-in                                                        #
# --------------------------------------------------------------------------- #
class _Cfg:
    allow_population_by_field_name = True
    allow_population_by_alias     = True
    by_alias                      = True


# --------------------------------------------------------------------------- #
# 1. Agreement meta-data                                                      #
# --------------------------------------------------------------------------- #
class AgreementType(BaseModel):
    value: Literal[
        "NDA", "PILOT", "AMENDMENT", "SOW", "ORDER FORM", "MASTER AGREEMENT", "RENEWAL", "Other?"
    ] = Field(
        ...,
        alias="Agreement Type",
        description=f"""Select the most applicable agreement type. You can use the filepath name as well as the text.

                    Guidelines:
                    * If the document is a standalone addendum or does not fit into any of the other categories, choose 'Other?'.
                    * PILOT includes POCs (proof of concept)
                    * SOW is a statement of work
                    * MASTER AGREEMENT includes contracts like MSA, SOFTWARE AGREEMENT, SAAS, PROFESSIONAL SERVICES, ONLINE TERMS etc.
                    """,
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Agreement Type"


class BackgroundChecksRequired(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Background Checks Required for all Personnel",
        description="Does the contract require the vendor to run background "
                    "checks on ALL personnel? Only relevant for professional "
                    "services; may be 'N/A?' otherwise.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Background Checks"


class BiometricLanguage(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Biometric Language",
        description="Indicates whether the text contains biometric-related language. Use 'Biometric' as a keyword."
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Biometric Language"


class BusinessAssociateAgreement(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Business Associate  Agreement (BAA)",
        description="Whether a HIPAA Business Associate Agreement is included "
                    "(typically healthcare-specific).",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "BAA"


class BusinessDownturnConsequences(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Business Downturn Consequences",
        description="Can Compass terminate / suspend services or licenses "
                    "without penalty if its own operations are reduced or "
                    "terminated?  May appear in Schedule Z on vendor paper.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Business Downturn Consequences"


class CanadianAddendum(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Canadian Addendum",
        description="Indicates presence of a Canada-specific addendum or section in the contract. This field is looking for whether Compass is able to do business with the vendor in Canada.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Canadian Addendum"


class ClientTerminationForConvenienceNoticePeriodDays(BaseModel):
    value: str = Field(
        ...,
        alias="Client's Termination for Convenience Right  Notice Period (Days)",
        description="Number of days’ notice the CLIENT must give to terminate for convenience. If the contract does not specify a notice period specificallyfor termination of the contract, return 'No'.",
    )
    explanation: str = Field(
        ...,
        description="Explanation of the notice period for termination of the contract. Explain your choices: in your retrieved context, the notice period itself has to specifically be about termination of the contract. ",
    )
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Client Termination For Convenience Notice Period Days"


class CounterpartyVendorName(BaseModel):
    value: str = Field(
        ...,
        alias="Counterparty/Vendor Name",
        description="Vendor’s legal name exactly as written in the document.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Vendor Name"


class DataPrivacyAddendum(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Data Processing/Privacy Addendum (DPA)",
        description="Presence of a Data Processing or Data Privacy Addendum/Agreement/Section in the contract.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "DPA"


class EffectiveDate(BaseModel):
    value: str = Field(
        ...,
        alias="Effective Date",
        description=f"""
        This attribute is the contract's defined Effective Date.  
        Consider the purpose of any dates listed in the contract:
        - If the date is when the contract takes effect, this is the effective date, use this.
        - If the contract does not list an effective date, use the date associated with the last signature.
        - If the contract does not list any relevant dates return "No".
        Output in this format: MM/DD/YYYY.
        """,
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Effective Date"


class NonRenewalNoticeDays(BaseModel):
    value: Optional[int] = Field(
        None,
        alias="If Auto Renewal, Notice of Non-Renewal Length (Days)",
        description="Advance notice (days) required to prevent an automatic renewal. Null if contract is not auto-renewing.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Non-Renewal Notice"


class InitialTermExpiration(BaseModel):
    value: str = Field(
        ...,
        alias="Initial Term Expiration Date",
        description="Expiration of the *initial* term (final date). "
                    "If Evergreen, capture end of initial term. "
                    "If perpetual → 'N/A'."
                    "If no end date is specified, but the initial term duration is known and any of the following dates are specified:"
                    "1. effective date, 2. signature date, 3. start date"
                    "then calculate the end date based on that information. ",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Initial Term Expiration"


class PaperType(BaseModel):
    value: Literal["Compass", "Vendor", "Vendor & Schedule Z"] = Field(
        ...,
        alias="Paper Type",
        description=f"""
        
        This field describes the business entity that drafted the contract, is it on Compass paper vs Vendor paper vs Vendor & Schedule Z.

        - Compass: The contract is drafted on Compass paper, meaning it is a standard contract template used by Compass.
        - Vendor: The contract is drafted on Vendor paper, meaning it is a contract template used by the vendor. It does not include a Schedule Z.
        - Vendor & Schedule Z: The contract is drafted on Vendor paper, but it includes a Schedule Z, which is an additional Compass template that may contain specific terms or conditions related to the contract.
        """,
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Paper Type"


class PaymentTerms(BaseModel):
    value: Optional[str] = Field(
        None,
        alias="Payment Terms",
        description="Payterm clauses/terms. For example, if the contract says payment is due upon 30 days from invoice, the value would be 'Net 30'. If no payment terms are specified, return 'No'.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Payment Terms"


class PriceIncreaseMechanism(BaseModel):
    value: Literal["3-5%", "5+%", "CPI", "CPI-W", "CPI-W or 3%", "Other","No"] = Field(
        ...,
        alias="Price Increase Mechanism",
        description=f"""
        How (or if) prices may increase during the contract term. 
        Select one from: '3-5%', '5+%', 'CPI', 'CPI-W', 'CPI-W or 3%', 'Other', 'No'. 
        - Use 'Other' if there is a price increase mechanism that is not one of the other options. 
        - Use 'No' if there is no price increase mechanism specified in the contract.
        - Use 'CPI' if the price increase mechanism is based on the Consumer Price Index (CPI).
        - Use 'CPI-W' if the price increase mechanism is based on the Consumer Price Index for Urban Wage Earners and Clerical Workers (CPI-W).
        - Use 'CPI-W or 3%' if the price increase mechanism is based on the Consumer Price Index for Urban Wage Earners and Clerical Workers (CPI-W) or 3%.
        - Use '3-5%' if the price increase mechanism is based on a 3-5% annual price increase.
        - Use '5+%' if the price increase mechanism is based on a 5+% annual price increase.
        - Do not use "CPI" as a default value when there is no mention of a price increase mechanism in the document.
        """,
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Price Increase Mechanism"


class QualityAssuranceLanguage(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Quality Assurance Language",
        description="Whether contract sets QA requirements (e.g., food safety).",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Quality Assurance"


class RenewalTerm(BaseModel):
    value: str = Field(
        ...,
        alias="Renewal Term",
        description="Length of each renewal term (if term type allows renewal). e.g. (3 years, 1 year, 12 months, etc.)",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Renewal Term"


class ServiceCredits(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Service Credits",
        description="""
                    Whether service-credit remedies are defined (N/A for Prof Svcs).
                    service-credit remedies are contractual provisions that outline the compensation or credits the customer receive if a 
                    service provider fails to meet agreed-upon service levels or performance standards
                    Do not confuse similar worded terms such as "credit memo" or "refund" with service credits.
                    """, 
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Service Credits"


class TermType(BaseModel):
    value: Literal[
        "Fixed Term",
        "Fixed Term with Renewal upon Mutual Agreement",
        "Automatic Renewal In Perpetuity (Evergreen)",
        "Limited Automatic Renewals",
        "Option To Unilaterally Renew",
        "Perpetual",
        "Contingent",
        "Other"
    ] = Field(
        ...,
        alias="Term Type",
        description=f"""Categorises how the contract term behaves (see detailed "
                    "definitions in worksheet).
                    
                        Please specify the type of term contemplated in the contract. 

                        Fixed Term: Select if term is a defined period of time following the effective date: This contract shall commence on the effective date and continue for a period of 12 months.

                        Fixed Term with Renewal upon Mutual Agreement

                        Automatic Renewal In Perpetuity Following Fixed Term: Select if there is a defined initial term, after which the agreement renews INDEFINITELY (or until terminated): Following the initial term, this contract will automatically for successive 12 month terms until either party notifies the other of its intent not to renew at least  90 days prior to the end of the then current term.

                        Limited Automatic Renewals Following Fixed Term: Select if there is a defined initial term followed by a SET NUMBER of automatic renewals: Following the initial term, this contract will automatically renew for two consecutive one-year terms unless terminated by either party in accordance with the termination section below.  

                        Option To Unilaterally Renew Following Fixed Term: Select if there is a defined initial term and one (or both) parties can unilaterally decide to renew the agreement - either a specific number of times or indefinitely. Either party may unilaterally extend this agreement for an additional 12-month term upon written notice to the other party no later than 30 days prior to the end of the initial term.

                        Perpetual: Select if there is no contemplated end date or if the agreement simply continues until terminated. Do NOT pick if there is an autorenewal period. This agreement is effective until terminated by either party.

                        Contingent: Select when it cannot be determined from the four corners both (1) when the contract term starts running or (2) when the contract expires due to one or both dates being tied to some external event. 
                        This Agreement shall be for a term of 3 years following commencement of services."" Note that the reviewer should select this option even if the expiration date is also uncertain. 
                        This Agreement shall be in effect for the longer of (1) five years or (2) the date on which all pending SOW's under this Agreement have expired 

                        Other:  Not addressed in Document"
                        """,
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Term Type"


class Biometrics(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Biometrics",
        description="Whether biometric data is processed under the contract.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Biometrics"


class DataSource(BaseModel):
    value: List[Literal["Employee", "Consumer", "Client", "Compass"]] = Field(
        ...,
        alias="Data Source",
        description="This field attributes the source of data as defined in the contract. It can be a list of multiple values, such as ['Compass', 'Client'] or ['Consumer']. If the contract does not specify data sources, return an empty list. Note that in this case, we are Compass.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Data Source"

class InvoiceFrequency(BaseModel):
    value: str = Field(
        ...,
        alias="Invoice Frequency",
        description="How often the vendor invoices Compass. If uncertain that the numbers found are actually for " \
        "invoice frequency, select 'No'.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Invoice Frequency"


# --------------------------------------------------------------------------- #
# Additional Fields                                                           #
# --------------------------------------------------------------------------- #

class FullyExecutedDualSignatures(BaseModel):
    value: Literal["Yes", "No"] = Field(
        ...,
        alias="Fully Executed With Dual Signatures",
        description="Whether the agreement is fully executed with dual signatures by both parties.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg):
        title = "Fully Executed With Dual Signatures"


class CounterpartySignature(BaseModel):
    value: Literal["Yes", "No"] = Field(
        ...,
        alias="Counterparty Signature",
        description="Whether the counterparty has signed the agreement.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg):
        title = "Counterparty Signature"


class Countersigned(BaseModel):
    value: Literal["Yes", "No"] = Field(
        ...,
        alias="Countersigned",
        description="Whether the document has been countersigned (i.e. a second signature applied).",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg):
        title = "Countersigned"




# --------------------------------------------------------------------------- #
# 2. Data-classification flags DEPRECATED                                     #
# --------------------------------------------------------------------------- #
class HighlySensitivePII(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Highly Sensitive PII",
        description="Whether Highly-Sensitive PII is involved.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Highly Sensitive PII"


class PCI(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="PCI",
        description="Payment Card Industry data present (Yes/No).",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "PCI"


class PHI(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="PHI",
        description="Protected Health Information processed (Yes/No).",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "PHI"


class SensitivePII(BaseModel):
    value: Literal["Yes", "No", "Removed"] = Field(
        ...,
        alias="Sensitive PII",
        description="Sensitive (but not highly-sensitive) PII processed (Yes/No).",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Sensitive PII"


# --------------------------------------------------------------------------- #
# 3. Risk-scoring                                                             #
# --------------------------------------------------------------------------- #
_Risk = Literal["LOW", "MEDIUM", "HIGH"]


class AgreementRiskNotes(BaseModel):
    value: str = Field(
        ...,
        alias="Agreement Risk Notes",
        description="Narrative explaining overall risk position and any Medium/High scores.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Agreement Risk Notes"


class MarketStabilityRiskScore(BaseModel):
    value: _Risk = Field(
        ...,
        alias="Financial / Organizational / Market Stability Risk Score",
        description="Risk score for vendor’s financial / market stability.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Market Stability Risk Score"


class MarketStabilityRiskNotes(BaseModel):
    value: str = Field(
        ...,
        alias="Financial / Organizational / Market Stability Risk Score Notes",
        description="Narrative explaining a Medium or High market-stability risk score.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Market Stability Risk Notes"


class StakeholderPerformanceRiskScore(BaseModel):
    value: _Risk = Field(
        ...,
        alias="VSO / Stakeholder Relationship / Performance Risk Score",
        description="Risk score for VSO stakeholder relationship / performance.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Stakeholder Performance Risk Score"


class StakeholderPerformanceRiskNotes(BaseModel):
    value: str = Field(
        ...,
        alias="VSO / Stakeholder Relationship / Performance Risk Score Notes",
        description="Narrative for a Medium or High stakeholder-performance score.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "Stakeholder Performance Risk Notes"


class VSOAgreementRiskScore(BaseModel):
    value: _Risk = Field(
        ...,
        alias="VSO Agreement Risk Score",
        description="Composite risk score for the overall agreement.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "VSO Agreement Risk Score"


class VSORiskScore(BaseModel):
    value: _Risk = Field(
        ...,
        alias="VSO Risk Score",
        description="Overall VSO risk score.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "VSO Risk Score"


class VSORiskScoreNotes(BaseModel):
    value: str = Field(
        ...,
        alias="VSO Risk Score Notes",
        description="Narrative explaining a Medium or High VSO risk score.",
    )
    explanation: str
    source_pdf_file: Optional[str]
    class Config(_Cfg): title = "VSO Risk Score Notes"


class AgentState(MessagesState):
    # Final structured response from the agent
    messages: Annotated[list,add_messages]
    final_response: BaseModel


# Define the response format for the model
class FirstPageVisionParserStructuredOutput(BaseModel):
    paper_type: str
    paper_type_explanation: str

# Define the response format for the model
class VisionParserStructuredOutput(BaseModel):
    fully_executed_with_dual_signatures: str
    fully_executed_with_dual_signatures_explanation: str
