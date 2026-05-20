LEGAL_CATEGORIES = {

    "Corporate Law": [
        "fiduciary duty",
        "shareholder",
        "board of directors",
        "merger",
        "acquisition",
        "corporation",
        "corporate governance",
        "proxy statement",
        "hostile takeover",
        "securities",
        "insider trading",
        "derivative suit",
        "business judgment rule",
        "director liability",
        "officer liability",
        "stockholder",
        "equity financing",
        "venture capital",
        "dividend",
        "corporate restructuring",
        "bankruptcy",
        "chapter 11",
        "limited liability company",
        "llc",
        "partnership",
        "joint venture"
    ],

    "Criminal Law": [
        "murder",
        "homicide",
        "manslaughter",
        "assault",
        "battery",
        "robbery",
        "burglary",
        "theft",
        "fraud",
        "forgery",
        "criminal",
        "sentence",
        "conviction",
        "acquittal",
        "indictment",
        "defendant",
        "prosecution",
        "felony",
        "misdemeanor",
        "probation",
        "parole",
        "search and seizure",
        "fourth amendment",
        "warrant",
        "interrogation",
        "confession",
        "self-defense",
        "mens rea",
        "actus reus",
        "beyond reasonable doubt",
        "criminal conspiracy",
        "drug trafficking",
        "money laundering",
        "racketeering",
        "rico"
    ],

    "Contract Law": [
        "breach of contract",
        "agreement",
        "contract",
        "offer",
        "acceptance",
        "consideration",
        "damages",
        "specific performance",
        "performance",
        "nonperformance",
        "material breach",
        "anticipatory breach",
        "indemnification",
        "warranty",
        "arbitration",
        "force majeure",
        "liquidated damages",
        "termination clause",
        "confidentiality agreement",
        "nda",
        "good faith",
        "purchase agreement",
        "service agreement",
        "void contract",
        "voidable contract",
        "contract formation"
    ],

    "Employment Law": [
        "employment",
        "termination",
        "wrongful termination",
        "employee",
        "employer",
        "workplace",
        "discrimination",
        "harassment",
        "hostile work environment",
        "retaliation",
        "wages",
        "overtime",
        "labor union",
        "collective bargaining",
        "workplace safety",
        "occupational safety",
        "workers compensation",
        "minimum wage",
        "employment contract",
        "non compete",
        "whistleblower",
        "human resources",
        "unfair dismissal",
        "equal employment",
        "ada",
        "title vii",
        "fmla"
    ],

    "Constitutional Law": [
        "constitution",
        "constitutional",
        "amendment",
        "bill of rights",
        "due process",
        "equal protection",
        "freedom of speech",
        "first amendment",
        "second amendment",
        "fourth amendment",
        "fifth amendment",
        "eighth amendment",
        "judicial review",
        "strict scrutiny",
        "fundamental rights",
        "civil liberties",
        "search and seizure",
        "privacy rights",
        "establishment clause",
        "free exercise clause",
        "procedural due process",
        "substantive due process",
        "state action",
        "constitutional challenge"
    ],

    "Tort Law": [
        "tort",
        "negligence",
        "gross negligence",
        "liability",
        "strict liability",
        "injury",
        "personal injury",
        "damages",
        "duty of care",
        "breach of duty",
        "causation",
        "proximate cause",
        "defamation",
        "libel",
        "slander",
        "intentional infliction",
        "emotional distress",
        "medical malpractice",
        "malpractice",
        "product liability",
        "wrongful death",
        "premises liability",
        "comparative negligence",
        "punitive damages"
    ],

    "Intellectual Property Law": [
        "copyright",
        "trademark",
        "patent",
        "trade secret",
        "infringement",
        "licensing",
        "fair use",
        "dmca",
        "intellectual property",
        "patentability",
        "prior art",
        "royalty",
        "brand infringement",
        "counterfeit",
        "software patent",
        "creative commons",
        "cease and desist"
    ],

    "Family Law": [
        "divorce",
        "custody",
        "child support",
        "alimony",
        "spousal support",
        "marital property",
        "domestic violence",
        "adoption",
        "guardianship",
        "visitation",
        "family court",
        "prenup",
        "prenuptial agreement",
        "separation agreement",
        "parental rights"
    ],

    "Property Law": [
        "property",
        "real estate",
        "landlord",
        "tenant",
        "lease",
        "mortgage",
        "easement",
        "title dispute",
        "foreclosure",
        "zoning",
        "property rights",
        "eviction",
        "adverse possession",
        "deed",
        "real property",
        "boundary dispute",
        "housing"
    ],

    "Administrative Law": [
        "administrative agency",
        "regulation",
        "rulemaking",
        "administrative hearing",
        "judicial review",
        "agency action",
        "federal register",
        "compliance",
        "licensing board",
        "government agency",
        "administrative appeal",
        "public policy"
    ],

    "Tax Law": [
        "tax",
        "irs",
        "income tax",
        "corporate tax",
        "tax liability",
        "tax fraud",
        "deduction",
        "audit",
        "estate tax",
        "capital gains",
        "sales tax",
        "taxpayer",
        "withholding",
        "tax return"
    ],

    "Environmental Law": [
        "environmental",
        "pollution",
        "epa",
        "clean air act",
        "clean water act",
        "hazardous waste",
        "toxic substance",
        "environmental impact",
        "climate regulation",
        "emissions",
        "sustainability",
        "contamination",
        "natural resources"
    ],

    "Immigration Law": [
        "immigration",
        "visa",
        "green card",
        "asylum",
        "citizenship",
        "deportation",
        "removal proceedings",
        "refugee",
        "naturalization",
        "border patrol",
        "immigration status"
    ],

    "Bankruptcy Law": [
        "bankruptcy",
        "chapter 7",
        "chapter 11",
        "chapter 13",
        "debtor",
        "creditor",
        "insolvency",
        "automatic stay",
        "liquidation",
        "reorganization",
        "bankruptcy estate"
    ],

    "Evidence Law": [
        "evidence",
        "hearsay",
        "admissibility",
        "witness testimony",
        "expert witness",
        "burden of proof",
        "cross examination",
        "authentication",
        "relevance",
        "privilege",
        "chain of custody"
    ],

    "Civil Procedure": [
        "motion to dismiss",
        "summary judgment",
        "class action",
        "standing",
        "jurisdiction",
        "venue",
        "discovery",
        "pleading",
        "civil procedure",
        "complaint",
        "injunction",
        "temporary restraining order",
        "appeal",
        "remand",
        "default judgment"
    ]
}

class LegalClassifier:

    def classify(
        self,
        text
    ):

        text_lower = text.lower()

        scores = {}

        for category, keywords in (
            LEGAL_CATEGORIES.items()
        ):

            score = 0

            for keyword in keywords:

                if keyword in text_lower:
                    score += 1

            scores[category] = score

        best_category = max(
            scores,
            key=scores.get
        )

        if scores[best_category] == 0:
            return "Unknown"

        return best_category
