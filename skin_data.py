# Skin conditions database based on dermatological research

SKIN_CONDITIONS = {
    "acne": {
        "name": "Acne / Pimples",
        "description": "Most common skin condition causing pimples, blackheads, whiteheads",
        "severity_levels": ["mild", "moderate", "severe"],
        "affected_areas": ["forehead", "cheeks", "chin", "nose", "back"],
        "treatments": {
            "creams": ["Benzoyl peroxide cream", "Azelaic acid cream", "Topical retinoids", "Clindamycin cream"],
            "soaps": ["Benzoyl peroxide soap", "Salicylic acid soap", "Tea tree oil soap"],
            "tablets": ["Isotretinoin (severe)", "Erythromycin", "Tetracycline"],
            "serums": ["Niacinamide serum", "Salicylic acid serum", "Vitamin C serum"]
        },
        "diet": {
            "eat": ["Green leafy vegetables", "Omega-3 rich foods", "Probiotics", "Zinc-rich foods", "Antioxidant fruits"],
            "avoid": ["Dairy products", "High sugar foods", "Processed foods", "Oily junk food", "High glycemic index foods"]
        },
        "lifestyle": ["Keep face clean", "Change pillowcases weekly", "Don't pop pimples", "Use non-comedogenic products"],
        "see_doctor_if": "Acne doesn't improve in 3 months or is severe"
    },
    "eczema": {
        "name": "Eczema (Atopic Dermatitis)",
        "description": "Red, itchy, inflamed dry skin condition",
        "treatments": {
            "creams": ["Hydrocortisone cream", "Steroid creams", "Moisturizing creams", "Tacrolimus ointment"],
            "soaps": ["Fragrance-free soap", "Neutrogena Gentle Cleanser", "CeraVe Cream Soap"],
            "tablets": ["Antihistamines (for itching)", "Steroid pills (severe)"],
            "serums": ["Ceramide serum", "Hyaluronic acid serum"]
        },
        "diet": {
            "eat": ["Anti-inflammatory foods", "Probiotics", "Vitamin D rich foods", "Omega-3 fatty acids"],
            "avoid": ["Common allergens", "Gluten (if sensitive)", "Dairy", "Eggs (if allergic)", "Soy"]
        },
        "lifestyle": ["Moisturize regularly", "Avoid hot showers", "Wear soft cotton clothes", "Identify and avoid triggers"],
        "see_doctor_if": "Severe itching, infection signs, or skin doesn't heal"
    },
    "dark_circles": {
        "name": "Dark Circles",
        "description": "Darkening of skin under the eyes",
        "treatments": {
            "creams": ["Vitamin K cream", "Retinol eye cream", "Caffeine eye cream", "Kojic acid cream"],
            "soaps": ["Gentle cleanser"],
            "tablets": ["Iron supplements (if deficient)", "Vitamin C tablets"],
            "serums": ["Vitamin C serum", "Niacinamide serum", "Peptide eye serum"]
        },
        "diet": {
            "eat": ["Iron-rich foods", "Vitamin C foods", "Hydrating foods", "Cucumber", "Sleep adequately"],
            "avoid": ["Excess salt", "Alcohol", "Caffeine (excess)", "Processed foods"]
        },
        "lifestyle": ["Sleep 7-8 hours", "Use cold compress", "Elevate head while sleeping", "Stay hydrated", "Use SPF daily"],
        "see_doctor_if": "Dark circles accompanied by puffiness or vision changes"
    },
    "hyperpigmentation": {
        "name": "Hyperpigmentation / Dark Spots",
        "description": "Dark patches or spots on skin",
        "treatments": {
            "creams": ["Hydroquinone cream (2-4%)", "Azelaic acid cream", "Vitamin C cream", "Retinoid cream"],
            "soaps": ["Gentle brightening soap", "Kojic acid soap"],
            "tablets": ["Tranexamic acid (severe)", "Vitamin C supplements"],
            "serums": ["Vitamin C serum", "Niacinamide serum", "Alpha arbutin serum", "Kojic acid serum"]
        },
        "diet": {
            "eat": ["Vitamin C rich fruits", "Antioxidant foods", "Turmeric", "Green tea", "Tomatoes"],
            "avoid": ["Sun exposure without SPF", "Excess alcohol", "Processed foods"]
        },
        "lifestyle": ["Use SPF 30+ daily", "Avoid direct sun", "Wear protective clothing", "Don't pick at spots"],
        "see_doctor_if": "Dark spots change in size or shape, or are asymmetric"
    },
    "dry_skin": {
        "name": "Dry Skin (Xerosis)",
        "description": "Tight, flaky, rough, scaly skin condition",
        "treatments": {
            "creams": ["CeraVe moisturizing cream", "Cetaphil lotion", "Urea cream", "Glycerin cream"],
            "soaps": ["Cetaphil Gentle Cleanser", "Moisturizing soap", "Fragrance-free soap"],
            "tablets": ["Hydration supplements", "Omega-3 supplements"],
            "serums": ["Hyaluronic acid serum", "Glycerin serum", "Ceramide serum"]
        },
        "diet": {
            "eat": ["Drink 8+ glasses water", "Omega-3 rich foods", "Avocado", "Nuts and seeds", "Olive oil"],
            "avoid": ["Hot showers", "Harsh soaps", "Alcohol (skin drying)", "Too much caffeine"]
        },
        "lifestyle": ["Moisturize immediately after shower", "Use humidifier", "Avoid very hot water", "Pat dry gently"],
        "see_doctor_if": "Severe cracking, bleeding, or infection"
    },
    "oily_skin": {
        "name": "Oily Skin",
        "description": "Excess sebum production causing shiny skin",
        "treatments": {
            "creams": ["Oil-free moisturizer", "Niacinamide cream", "Salicylic acid cream"],
            "soaps": ["Salicylic acid face wash", "Neem face wash", "Tea tree face wash"],
            "tablets": ["Vitamin B5 supplements"],
            "serums": ["Niacinamide serum", "Salicylic acid serum", "Zinc serum"]
        },
        "diet": {
            "eat": ["Green vegetables", "Fruits rich in fiber", "Zinc-rich foods", "Omega-3 foods"],
            "avoid": ["Greasy fried foods", "High sugar foods", "Dairy", "Refined carbs"]
        },
        "lifestyle": ["Cleanse twice daily", "Use oil-free products", "Blotting papers", "Non-comedogenic makeup"],
        "see_doctor_if": "Oily skin accompanied by severe acne"
    },
    "psoriasis": {
        "name": "Psoriasis",
        "description": "Autoimmune disorder causing scaly plaques with silvery scales",
        "treatments": {
            "creams": ["Steroid creams", "Coal tar cream", "Salicylic acid cream", "Vitamin D analogue cream"],
            "soaps": ["Coal tar soap", "Salicylic acid soap", "Medicated soap"],
            "tablets": ["Methotrexate (severe)", "Systemic medications"],
            "serums": ["Moisturizing serum"]
        },
        "diet": {
            "eat": ["Anti-inflammatory foods", "Omega-3 rich fish", "Fruits and vegetables", "Turmeric", "Ginger"],
            "avoid": ["Alcohol", "Processed foods", "Red meat", "Dairy", "Gluten (if sensitive)"]
        },
        "lifestyle": ["Moisturize daily", "Manage stress", "Avoid skin injury", "Sun exposure in moderation"],
        "see_doctor_if": "Covers more than 10% of body or joints are affected"
    },
    "rosacea": {
        "name": "Rosacea",
        "description": "Chronic facial redness with visible blood vessels",
        "treatments": {
            "creams": ["Metronidazole cream", "Azelaic acid cream", "Anti-inflammatory creams"],
            "soaps": ["Gentle fragrance-free soap", "Sensitive skin cleanser"],
            "tablets": ["Antibiotic tablets (moderate-severe)", "Anti-inflammatory tablets"],
            "serums": ["Green tea serum", "Niacinamide serum"]
        },
        "diet": {
            "eat": ["Anti-inflammatory foods", "Omega-3 foods", "Green tea", "Probiotic foods"],
            "avoid": ["Hot drinks", "Spicy food", "Alcohol", "Hot baths", "Extreme temperatures"]
        },
        "lifestyle": ["Use SPF daily", "Avoid triggers", "Gentle skincare only", "Manage stress"],
        "see_doctor_if": "Redness spreading or eye rosacea symptoms"
    },
    "melasma": {
        "name": "Melasma",
        "description": "Dark brown patches typically on face",
        "treatments": {
            "creams": ["Hydroquinone cream", "Azelaic acid cream", "Vitamin C cream", "Retinoid cream"],
            "soaps": ["Gentle soap", "Brightening cleanser"],
            "tablets": ["Tranexamic acid (oral)", "Vitamin C tablets"],
            "serums": ["Vitamin C serum", "Alpha arbutin serum", "Kojic acid serum"]
        },
        "diet": {
            "eat": ["Vitamin C rich foods", "Antioxidant foods", "Folic acid foods"],
            "avoid": ["Sun without protection", "Hormonal triggers (consult doctor)"]
        },
        "lifestyle": ["Use SPF 50+ daily", "Avoid direct sun 10am-4pm", "Wear hats", "No tanning"],
        "see_doctor_if": "Melasma during pregnancy or not responding to treatment"
    },
    "contact_dermatitis": {
        "name": "Contact Dermatitis",
        "description": "Redness and itching where skin touched an irritant",
        "treatments": {
            "creams": ["Hydrocortisone cream", "Corticosteroid cream", "Calamine lotion"],
            "soaps": ["Stop irritant soap", "Gentle fragrance-free soap"],
            "tablets": ["Antihistamines", "Corticosteroid pills (severe)"],
            "serums": ["Soothing aloe serum"]
        },
        "diet": {
            "eat": ["Anti-histamine foods", "Anti-inflammatory foods"],
            "avoid": ["Known allergen foods"]
        },
        "lifestyle": ["Identify and avoid triggers", "Wear gloves when handling irritants", "Patch test new products"],
        "see_doctor_if": "Severe reaction, blistering, or not improving in 3 days"
    }
}

DIET_TIPS = {
    "general": {
        "eat": [
            "Drink 8-10 glasses of water daily",
            "Eat colorful fruits and vegetables",
            "Include omega-3 fatty acids (fish, flaxseeds, walnuts)",
            "Consume probiotic foods (curd, yogurt)",
            "Add turmeric and ginger to diet",
            "Eat zinc-rich foods (pumpkin seeds, chickpeas)",
            "Include Vitamin C foods (amla, citrus fruits, bell peppers)"
        ],
        "avoid": [
            "Reduce sugar and refined carbohydrates",
            "Limit dairy products",
            "Avoid processed and packaged foods",
            "Reduce alcohol consumption",
            "Limit coffee/tea (excess dehydrates skin)",
            "Avoid deep fried foods",
            "Minimize spicy foods if skin is sensitive"
        ]
    }
}

PRODUCTS_DB = {
    "budget": {
        "cleanser": ["Himalaya Neem Face Wash (₹130)", "Garnier Micellar Water (₹200)", "Cetaphil Gentle Cleanser (₹380)"],
        "moisturizer": ["Nivea Soft (₹120)", "Biotique Bio Coconut (₹180)", "Ponds Super Light Gel (₹200)"],
        "sunscreen": ["Lotus Herbals SPF 50 (₹250)", "Lakme Sun Expert SPF 50 (₹200)", "Biotique SPF 40 (₹150)"],
        "serum": ["Minimalist Niacinamide 10% (₹599)", "The Derma Co Vitamin C (₹499)", "Plum 15% Vitamin C (₹695)"]
    },
    "mid_range": {
        "cleanser": ["La Roche Posay Effaclar (₹990)", "Simple Kind to Skin (₹450)", "Neutrogena Deep Clean (₹380)"],
        "moisturizer": ["Neutrogena Hydro Boost (₹995)", "L'Oreal Revitalift (₹850)", "Olay Total Effects (₹1299)"],
        "sunscreen": ["La Roche Posay SPF 50 (₹1500)", "Neutrogena Ultra Sheer (₹850)", "Bioderma Photoderm (₹1200)"],
        "serum": ["Dot & Key Vitamin C (₹895)", "mCaffeine Coffee Face Serum (₹699)", "COSRX BHA (₹1500)"]
    },
    "premium": {
        "cleanser": ["CeraVe Hydrating Cleanser (₹2000)", "Kiehl's Calendula (₹3500)", "Fresh Soy Face Cleanser (₹3500)"],
        "moisturizer": ["Clinique Moisturizing Lotion (₹3000)", "Cetaphil Moisturizing Cream (₹1500)", "CeraVe PM Facial Moisturizer (₹2500)"],
        "sunscreen": ["SkinCeuticals Physical Fusion (₹5000)", "EltaMD UV Clear (₹4500)", "Heliocare 360° (₹3500)"],
        "serum": ["The Ordinary Hyaluronic Acid (₹1500)", "Paula's Choice BHA (₹3200)", "SkinCeuticals CE Ferulic (₹15000)"]
    }
}
