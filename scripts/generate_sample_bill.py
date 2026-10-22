"""
Generate sample legislative bills in PDF format using PyMuPDF.
Includes realistic headers, footers, page numbers, line numbers,
and section titles to test extraction and cleaning pipelines.
"""

import os
import pymupdf

def create_sample_legislative_bill(output_path: str = "data/sample_bill_clean_energy.pdf") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = pymupdf.open()
    
    pages_content = [
        {
            "page_num": 1,
            "header": "118TH CONGRESS  •  2D SESSION  •  H.R. 4082",
            "footer": "Page 1 of 5  •  CONGRESSIONAL RECORD - LEGISLATIVE DRAFT",
            "sections": [
                ("TITLE AND ENACTING CLAUSE", 
                 "IN THE HOUSE OF REPRESENTATIVES\n\n"
                 "A BILL\n\n"
                 "To accelerate renewable energy adoption while safeguarding economic vitality for small businesses, "
                 "rural agricultural producers, and vulnerable wage-earning families.\n\n"
                 "Be it enacted by the Senate and House of Representatives of the United States of America in Congress assembled,"),
                ("SECTION 1. SHORT TITLE; TABLE OF CONTENTS.",
                 "(a) Short Title.—This Act may be cited as the 'Clean Energy Transition and Small Business Economic Resilience Act of 2026'.\n"
                 "(b) Purpose.—The primary objective is to allocate federal grant matching, reduce localized electricity tariffs, "
                 "and provide targeted micro-enterprise transition funds."),
                ("SECTION 2. FINDINGS AND DECLARATIONS OF IMPACT.",
                 "(a) Small Business Vulnerability.—Commercial electricity rate fluctuations disproportionately impact commercial enterprises "
                 "employing fewer than 50 individuals, particularly food service, retail, and regional manufacturing.\n"
                 "(b) Demographic Disparities.—Rural low-income households allocate up to 14.2 percent of disposable income to energy expenditures, "
                 "representing a severe energy burden that necessitates direct public assistance.")
            ]
        },
        {
            "page_num": 2,
            "header": "118TH CONGRESS  •  2D SESSION  •  H.R. 4082",
            "footer": "Page 2 of 5  •  CONGRESSIONAL RECORD - LEGISLATIVE DRAFT",
            "sections": [
                ("SECTION 3. MICRO-ENTERPRISE CLEAN ENERGY TRANSITION GRANTS.",
                 "(a) Establishment of Grant Facility.—The Secretary of Energy, in consultation with the Small Business Administration, "
                 "shall establish the 'Commercial Decarbonization Incentive Program'.\n"
                 "(b) Eligible Entities.—An entity is eligible for a competitive grant under this section if the entity:\n"
                 "  (1) Employs not more than 40 full-time equivalent employees;\n"
                 "  (2) Maintains an average annual gross revenue below $4,500,000 for the preceding 3 fiscal years;\n"
                 "  (3) Operates primarily in designated rural or economically distressed municipal corridors.\n"
                 "(c) Grant Amounts.—Individual grants shall not exceed $75,000 per commercial establishment, "
                 "or 80 percent of qualified capital costs for heat pump, solar photovoltaic, or commercial battery storage installation.\n"
                 "(d) Fast-Track Disbursements.—Applications submitted by women-, veteran-, and minority-owned small businesses shall "
                 "receive priority review and expedited determination within 21 business days of receipt.")
            ]
        },
        {
            "page_num": 3,
            "header": "118TH CONGRESS  •  2D SESSION  •  H.R. 4082",
            "footer": "Page 3 of 5  •  CONGRESSIONAL RECORD - LEGISLATIVE DRAFT",
            "sections": [
                ("SECTION 4. WORKFORCE RETRAINING AND DISPLACED WORKER STIPENDS.",
                 "(a) Displaced Worker Wage Guarantee.—Eligible energy workers who experience employment termination or reduction in hours "
                 "due to fossil-fuel thermal generation facility closures shall be entitled to:\n"
                 "  (1) A transitional stipend of $2,400 per month for up to 18 consecutive months;\n"
                 "  (2) 100 percent tuition reimbursement for certified technical apprenticeships or vocational certification at community colleges;\n"
                 "  (3) Continuing healthcare coverage premium subsidies under COBRA for a duration of 24 months.\n"
                 "(b) Local Union Apprenticeships.—Grants shall be awarded to accredited regional labor organizations and community colleges "
                 "to establish advanced high-voltage line worker, wind turbine technician, and battery storage technician training facilities.\n"
                 "(c) Senior Worker Protections.—Workers aged 55 and older shall be offered an expedited bridge-to-pension option "
                 "funded jointly through federal clean energy transition reserves.")
            ]
        },
        {
            "page_num": 4,
            "header": "118TH CONGRESS  •  2D SESSION  •  H.R. 4082",
            "footer": "Page 4 of 5  •  CONGRESSIONAL RECORD - LEGISLATIVE DRAFT",
            "sections": [
                ("SECTION 5. MUNICIPAL INFRASTRUCTURE AND RESIDENTIAL UTILITY RELIEF.",
                 "(a) Low-Income Household Utility Bill Caps.—The Department of Housing and Urban Development shall disburse direct block grants "
                 "to local utility providers to ensure that no residential customer with an income below 200 percent of the federal poverty level "
                 "is charged more than 5 percent of gross household income for home heating and electricity.\n"
                 "(b) Rural Community Solar Co-Ops.—Allocates $500,000,000 across fiscal years 2026 through 2029 for shared agricultural community solar arrays. "
                 "Farmers who dedicate uncultivated land to community solar generation shall receive an annual property tax credit of $1,200 per acre.\n"
                 "(c) Public School Weatherization.—Provides emergency funding for HVAC filtration and insulation upgrades in public school districts "
                 "where over 60 percent of enrolled students qualify for the National School Lunch Program.")
            ]
        },
        {
            "page_num": 5,
            "header": "118TH CONGRESS  •  2D SESSION  •  H.R. 4082",
            "footer": "Page 5 of 5  •  CONGRESSIONAL RECORD - LEGISLATIVE DRAFT",
            "sections": [
                ("SECTION 6. COMPLIANCE, TRANSPARENCY, AND EFFECTIVE DATES.",
                 "(a) Reporting Requirements.—Not later than 180 days after the date of enactment, the Comptroller General of the United States "
                 "shall submit to the Committee on Energy and Commerce of the House of Representatives an initial audit regarding distribution equity.\n"
                 "(b) Anti-Gouging Provisions.—Retail electricity suppliers participating in federal subsidy programs are strictly prohibited "
                 "from raising residential baseline kWh tariffs for a period of 36 months following grant receipt.\n"
                 "(c) Severability.—If any provision of this Act or its application is held invalid, the remainder of the Act shall not be affected.\n"
                 "(d) Effective Date.—Except as otherwise explicitly specified, this Act shall take effect on January 1, 2027.")
            ]
        }
    ]
    
    for p_data in pages_content:
        page = doc.new_page(width=612, height=792)  # Standard Letter size
        
        # Header (Top)
        page.insert_text(
            (72, 40),
            p_data["header"],
            fontsize=9,
            color=(0.4, 0.4, 0.4),
            fontname="helv"
        )
        page.draw_line((72, 48), (540, 48), color=(0.7, 0.7, 0.7), width=0.5)
        
        # Footer (Bottom)
        page.draw_line((72, 744), (540, 744), color=(0.7, 0.7, 0.7), width=0.5)
        page.insert_text(
            (72, 758),
            p_data["footer"],
            fontsize=8.5,
            color=(0.4, 0.4, 0.4),
            fontname="helv"
        )
        
        # Body text
        y = 75
        for title, body in p_data["sections"]:
            page.insert_text((72, y), title, fontsize=11, color=(0.1, 0.1, 0.2), fontname="hebo")
            y += 18
            
            words = body.split()
            current_line = []
            for word in words:
                test_line = " ".join(current_line + [word])
                if len(test_line) > 68 or "\n" in word:
                    line_str = " ".join(current_line)
                    page.insert_text((72, y), line_str, fontsize=10, color=(0.15, 0.15, 0.15), fontname="helv")
                    y += 15
                    current_line = [word.replace("\n", "")]
                else:
                    current_line.append(word)
            if current_line:
                page.insert_text((72, y), " ".join(current_line), fontsize=10, color=(0.15, 0.15, 0.15), fontname="helv")
                y += 24
                
    doc.save(output_path)
    doc.close()
    print(f"Generated sample legislative bill at: {output_path} ({len(pages_content)} pages)")
    return output_path


def create_sample_healthcare_bill(output_path: str = "data/sample_bill_healthcare_senior_care.pdf") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = pymupdf.open()
    
    pages_content = [
        {
            "page_num": 1,
            "header": "118TH CONGRESS  •  2D SESSION  •  S. 2190",
            "footer": "Page 1 of 3  •  SENATE CALENDAR NO. 412",
            "sections": [
                ("TITLE AND ENACTING CLAUSE",
                 "IN THE SENATE OF THE UNITED STATES\n\nA BILL\n\n"
                 "To strengthen critical access hospitals in medically underserved rural communities and cap out-of-pocket prescription drug costs for senior citizens.\n\n"
                 "Be it enacted by the Senate and House of Representatives of the United States of America in Congress assembled,"),
                ("SECTION 1. SHORT TITLE.",
                 "This Act may be cited as the 'Rural Healthcare Access and Senior Prescription Affordability Act of 2026'.")
            ]
        },
        {
            "page_num": 2,
            "header": "118TH CONGRESS  •  2D SESSION  •  S. 2190",
            "footer": "Page 2 of 3  •  SENATE CALENDAR NO. 412",
            "sections": [
                ("SECTION 2. SENIOR PRESCRIPTION MEDICATION CO-PAY CAPS.",
                 "(a) Monthly Cost Ceiling.—Under Medicare Part D, a participating beneficiary aged 65 or older shall not be required to pay "
                 "a co-payment exceeding $35 for a 30-day supply of insulin, cardiovascular maintenance therapeutics, or inhalers.\n"
                 "(b) Elimination of Deductibles.—The standard Medicare deductible shall not apply to qualifying tier-1 life-saving chronic medications.\n"
                 "(c) Penalty for Non-Compliance.—Pharmaceutical manufacturers that artificially elevate wholesale acquisition costs "
                 "above the regional inflation adjustment rate shall be subject to a 95 percent excise rebate penalty.")
            ]
        },
        {
            "page_num": 3,
            "header": "118TH CONGRESS  •  2D SESSION  •  S. 2190",
            "footer": "Page 3 of 3  •  SENATE CALENDAR NO. 412",
            "sections": [
                ("SECTION 3. RURAL CRITICAL ACCESS HOSPITAL CAPITAL GRANTS.",
                 "(a) Capital Assistance Facility.—The Administrator of the Health Resources and Services Administration (HRSA) "
                 "shall award non-matching grants of up to $2,500,000 per facility to non-profit hospitals located in counties with fewer than 35,000 residents.\n"
                 "(b) Allowable Expenditures.—Funds may be utilized for emergency room modernization, digital diagnostic telemetry, "
                 "and nurse recruitment signing bonuses not to exceed $25,000 per registered nurse.\n"
                 "(c) Mobile Telehealth Outreach.—Grants up to $350,000 shall be made available to local municipal public libraries "
                 "to deploy private, HIPAA-compliant virtual telemedicine consultation kiosks.")
            ]
        }
    ]
    
    for p_data in pages_content:
        page = doc.new_page(width=612, height=792)
        page.insert_text((72, 40), p_data["header"], fontsize=9, color=(0.4, 0.4, 0.4), fontname="helv")
        page.draw_line((72, 48), (540, 48), color=(0.7, 0.7, 0.7), width=0.5)
        page.draw_line((72, 744), (540, 744), color=(0.7, 0.7, 0.7), width=0.5)
        page.insert_text((72, 758), p_data["footer"], fontsize=8.5, color=(0.4, 0.4, 0.4), fontname="helv")
        
        y = 75
        for title, body in p_data["sections"]:
            page.insert_text((72, y), title, fontsize=11, color=(0.1, 0.1, 0.2), fontname="hebo")
            y += 18
            words = body.split()
            current_line = []
            for word in words:
                test_line = " ".join(current_line + [word])
                if len(test_line) > 68 or "\n" in word:
                    line_str = " ".join(current_line)
                    page.insert_text((72, y), line_str, fontsize=10, color=(0.15, 0.15, 0.15), fontname="helv")
                    y += 15
                    current_line = [word.replace("\n", "")]
                else:
                    current_line.append(word)
            if current_line:
                page.insert_text((72, y), " ".join(current_line), fontsize=10, color=(0.15, 0.15, 0.15), fontname="helv")
                y += 24
                
    doc.save(output_path)
    doc.close()
    print(f"Generated sample legislative bill at: {output_path} ({len(pages_content)} pages)")
    return output_path

if __name__ == "__main__":
    create_sample_legislative_bill()
    create_sample_healthcare_bill()
