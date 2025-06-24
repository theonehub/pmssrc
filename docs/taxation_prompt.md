You are to design and implement a modular Indian Payroll & Taxation system following SOLID principles.

### Objective
Build a payroll module where:
1. Employers can define custom salary components.
2. Employees are assigned a monthly salary structure using these components.
3. A tax engine computes monthly TDS and annual liability as per Indian income tax rules (including slabs, deductions, exemptions).
4. The system supports payslip generation, Form 16, and FVU (24Q) file generation.

### Architecture Requirements
- **Backend**: FastAPI
- **Frontend**: React.js
- **Database**: MongoDB
- **Design Principles**: Must follow SOLID design
- **Domain Separation**: Break logic into clean service layers (e.g., ComponentService, TaxService)
- **API Layer**: RESTful endpoints grouped by responsibility
- **Validation**: Pydantic models
- **Formula Evaluation**: Safe parsing of expressions using symbols (e.g., `"BASIC * 0.4"` for HRA)

---

### Module 1: Employer Salary Component Configuration
- Employer defines components like BASIC, HRA, LTA, Bonus, PF
- Each component has:
  - Code, Name, Value Type (Fixed / Formula / Variable)
  - Formula (optional)
  - Is Taxable (yes/no)
  - Exemption section (e.g., 10(13A) for HRA)
  - Type: Earning / Deduction / Reimbursement

---

### Module 2: Employee Salary Assignment
- Employees are assigned components with values or formulas
- Structure is stored monthly (not annually)
- Support `effective_from` and `effective_to` for salary revisions

---

### Module 3: Tax Computation Engine
- Compute gross monthly and annual income
- Apply:
  - Exemptions (HRA, LTA, etc.)
  - Standard deduction (₹50,000)
  - Deductions under 80C, 80D, etc.
  - Rebate under Section 87A
- Support both Old and New Regime
- Monthly TDS projection and deduction

---

### Module 4: Payroll Processing
- Monthly payslip generation
- Calculation of earnings, deductions, and net pay
- Maintain monthly tax ledger

---

### Module 5: Reporting
- Generate Form 16
- Generate FVU (24Q) TDS returns
- Download monthly payslip, tax summary

---

### Technical Implementation
- Follow SOLID Principles:
  - **S**: Each class/service should have a single responsibility
  - **O**: Components should be extendable (new exemptions, regimes)
  - **L**: Subclasses/interfaces like tax regimes should be interchangeable
  - **I**: Use small interfaces for formula resolvers, tax policies
  - **D**: Use dependency injection for services (component resolver, tax engine)

- Use service classes like:
  - `SalaryComponentService`
  - `EmployeeSalaryService`
  - `TaxComputationService`
  - `PayslipService`

- Formula engine must allow referencing other components (e.g., HRA = BASIC * 0.4)

---

### Frontend
- React + MUI
- Employer interface to configure components
- Admin panel to assign structures to employees
- Employee portal for viewing payslips, tax summary, Form 16

---

### Optional Add-ons
- Investment Declaration UI
- Document uploads for proof (LIC, Rent Agreement, etc.)
- Auto-switch to New/Old regime based on employee choice
