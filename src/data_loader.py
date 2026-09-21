"""
Data Loader Module for Sanskrit Shloka Analysis RAG System.
Extracts Sanskrit texts, grammatical analyses, and methodology from source PDFs.
Maintains pristine source data integrity and creates structured representations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.schemas import ShlokaData

def extract_pdf_pages(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text page-by-page from a PDF file using pypdf if available.
    Returns a list of dicts: [{"page_number": int, "text": str}]
    """
    pages_data = []
    if not pdf_path.exists():
        return pages_data

    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append({
                "page_number": idx + 1,
                "text": text
            })
    except Exception as e:
        print(f"[Warning] PDF extraction fallback for {pdf_path.name}: {e}")

    return pages_data


def get_curated_chapter1_shlokas() -> List[Dict[str, Any]]:
    """
    Returns curated, high-fidelity structured data for Shlokas 1 to 17 of
    Sushruta Samhita, Nidana Sthana, Chapter 1: Vatavyadhi Nidana,
    extracted faithfully from 'CHAPTER 1- VATAVYADHI NIDANA.pdf'.
    """
    return [
        {
            "id": "sushruta_nidana_ch1_shloka_001_002",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 1,
            "shloka_number_display": "1-2",
            "text": "अथातो वातव्याधिदानं व्याख्यास्यामः ||१||\nयथोवाच भगवान् धन्वन्तरिः ||२||",
            "transliteration": "athāto vātavyādhidānaṁ vyākhyāsyāmaḥ ||1||\nyathovāca bhagavān dhanvantariḥ ||2||",
            "english_title": "Pledge to explain the diagnosis of Vata disorders as spoken by Dhanvantari",
            "associated_pages": [1, 2, 3],
            "padavibhaga": "अथ | अतः | वात-व्याधि-निदानम् | व्याख्यास्यामः ॥ १ ॥ यथा | उवाच | भगवान् | धन्वन्तरिः ॥ २ ॥",
            "anvaya": "यथा भगवान् धन्वन्तरिः उवाच, (तथा) अथ अतः (वयम्) वातव्याधिदानं व्याख्यास्यामः।",
            "shlokartha": "अथ (इदानीम्), अतः (अस्मात् कारणात्), वातव्याधिदानम् (वातजन्यरोगकारणम्), व्याख्यास्यामः (विस्तरेण कथयिष्यामः)। यथा (येन प्रकारेण), भगवान् (ऐश्वर्यवान्), धन्वन्तरिः (देववैद्यः), उवाच (कथितवान्)। Now, therefore, we shall explain the etiology and diagnosis of Vata-related diseases, exactly as Lord Dhanvantari has spoken/instructed.",
            "bhavartha": "अत्र आचार्यः सुश्रुत-संहितायाः निदानस्थानस्य आरम्भं करोति। 'अथ' इति शब्दः मङ्गलवाचकः अस्ति, यः ग्रन्थस्य निर्विघ्नसमाप्तये प्रयुज्यते। 'अतः' इति पदेन पूर्वोक्त-अध्यायानां सङ्गतिः दर्शिता। अत्र लेखकः प्रतिजानीते यत् सः वातव्याधीनां कारणानां (निदानस्य) वर्णनं करिष्यति। विशेषतः सः उद्घोषयति यत् अयं उपदेशः तस्य स्वकपोलकल्पितः नास्ति, अपितु भगवान् धन्वन्तरिः यथा उपदिष्टवान्, तथैव सः अत्र उपस्थापयिष्यति। अनेन ग्रन्थस्य प्रामाणिकता सिद्धा भवति।",
            "grammar_details": {
                "sandhi": [
                    {"pada": "अथातो", "split": "अथ + अतः", "type": "सवर्णदीर्घः & उत्वम्", "rule": "'अ' + 'अ' = 'आ'; Visarga of 'अतः' becomes 'ओ' before 'व'"},
                    {"pada": "यथोवाच", "split": "यथा + उवाच", "type": "गुण-सन्धिः", "rule": "'आ' + 'उ' = 'ओ'"}
                ],
                "samasa": [
                    {"pada": "वातव्याधिदानम्", "vigraha": "वातस्य व्याधयः (वातव्याधयः), तेषां निदानम्", "type": "षष्ठी-तत्पुरुषः", "meaning": "Etiology of diseases caused by Vata"}
                ],
                "avyaya": [
                    {"pada": "अथ", "meaning": "मङ्गलार्थे, अधिकारार्थे च (Auspicious beginning / Now)"},
                    {"pada": "अतः", "meaning": "हेत्वर्थे, आनन्तर्यार्थे च (Therefore / Following this)"},
                    {"pada": "यथा", "meaning": "प्रकारार्थे (As / In the manner)"}
                ],
                "shabdaroopa": [
                    {"pada": "वातव्याधिदानम्", "pratipadika": "वातव्याधिदान", "linga": "नपुंसकलिंगम्", "vibhakti": "द्वितीया", "vachana": "एकवचनम्", "karaka": "कर्म"},
                    {"pada": "भगवान्", "pratipadika": "भगवत्", "linga": "पुंल्लिंगम्", "vibhakti": "प्रथमा", "vachana": "एकवचनम्", "karaka": "कर्ता"},
                    {"pada": "धन्वन्तरिः", "pratipadika": "धन्वन्तरि", "linga": "पुंल्लिंगम्", "vibhakti": "प्रथमा", "vachana": "एकवचनम्", "karaka": "कर्ता (विशेष्य)"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "व्याख्यास्यामः", "dhatu": "ख्या (वि + आ)", "gana": "अदादि", "meaning": "To explain / कथने", "lakara": "लृट्", "purusha": "उत्तमः", "vachana": "बहुवचनम्"},
                    {"kriyapada": "उवाच", "dhatu": "वच्", "gana": "अदादि", "meaning": "Spoke / परिभाषणे", "lakara": "लिट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"}
                ],
                "kridanta": [
                    {"pada": "निदानम्", "prakriti": "नि + दा", "pratyaya": "ल्युट्", "type": "कृदन्त", "meaning": "Primary cause / Diagnosis"},
                    {"pada": "भगवान्", "prakriti": "भग", "pratyaya": "मतुप्", "type": "तद्धित", "meaning": "Possessing divine opulence"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_003_004",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 3,
            "shloka_number_display": "3-4",
            "text": "धन्वन्तरिं धर्मभृतां वरिष्ठममृतोद्भवम् |\nचरणावुपसङ्गृह्य सुश्रुतः परिपृच्छति ||३||\nवायोः प्रकृतिभूतस्य व्यापन्नस्य च कोपनैः |\nस्थानं कर्म च रोगांश्च वद मे वदतां वर ||४||",
            "transliteration": "dhanvantariṁ dharmabhṛtāṁ variṣṭhamamṛtodbhavam |\ncaraṇāvupasaṅgṛhya suśrutaḥ paripṛcchati ||3||\nvāyoḥ prakṛtibhūtasya vyāpannasya ca kopanaiḥ |\nsthānaṁ karma ca rogāṁśca vada me vadatāṁ vara ||4||",
            "english_title": "Sushruta's humble inquiry to Lord Dhanvantari about natural and vitiated Vata",
            "associated_pages": [4, 5, 6, 7],
            "padavibhaga": "धन्वन्तरिम् | धर्मभृताम् | वरिष्ठम् | अमृत-उद्भवम् | चरणौ | उपसङ्गृह्य | सुश्रुतः | परिपृच्छति || वायोः | प्रकृति-भूतस्य | व्यापन्नस्य | च | कोपनैः | स्थानम् | कर्म | च | रोगान् | च | वद | मे | वदताम् | वर ||",
            "anvaya": "धर्मभृतां वरिष्ठम् अमृतोद्भवं धन्वन्तरिं चरणौ उपसङ्गृह्य सुश्रुतः परिपृच्छति। (सः प्रार्थयति—) हे वदतां वर! प्रकृतिभूतस्य व्यापन्नस्य च वायोः स्थानं कर्म कोपनैः (उत्पन्नान्) रोगांश्च मे वद।",
            "shlokartha": "Having respectfully touched the feet of Lord Dhanvantari—the foremost among the upholders of Dharma and the one who emerged with nectar—Suśruta inquires: 'O best among speakers! Please explain to me the locations, functions, and the diseases caused by the aggravation of Vāyu (wind humor), both in its natural and vitiated states.'",
            "bhavartha": "अत्र आयुर्वेदशास्त्रस्य प्रवर्तकं धन्वन्तरिं प्रति सुश्रुतस्य जिज्ञासा प्रदर्शिता। शिष्यः सुश्रुतः विनयेन गुरुचरणौ स्पृष्ट्वा वायोः तत्त्वं ज्ञातुम् इच्छति। वातः शरीरस्य मुख्यं तत्त्वम्। तस्य प्राकृतावस्था (Health) वैकृतावस्था (Disease) च उभयम् अपि ज्ञातव्यम्। कोपनैः हेतुभिः वायुः कथं कुप्यति, तस्य स्थानानि कानि, कर्माणि कानि, तथा च तेन उत्पन्नाः रोगाः के इति प्रश्नाः अत्र सन्ति। 'वदतां वर' इति सम्बोधनेन धन्वन्तरेः वाक्पटुत्वं ज्ञानश्रेष्ठत्वं च सूचितम्।",
            "grammar_details": {
                "sandhi": [
                    {"pada": "धन्वन्तरिं धर्मभृतां", "split": "धन्वन्तरिम् धर्मभृताम्", "type": "अनुस्वारः", "rule": "मान्तस्य पदस्य अनुस्वारः"},
                    {"pada": "अमृतोद्भवम्", "split": "अमृत + उद्भवम्", "type": "गुण-सन्धिः", "rule": "अ + उ = ओ"},
                    {"pada": "चरणावुपसङ्गृह्य", "split": "चरणौ + उपसङ्गृह्य", "type": "अयादि-सन्धिः", "rule": "औ-कारस्य 'आव्' आदेशः"},
                    {"pada": "रोगांश्च", "split": "रोगान् + च", "type": "श्चुत्वम् / रुत्वम्", "rule": "न्-कारस्य विसर्गे, ततः शकारे"}
                ],
                "samasa": [
                    {"pada": "धर्मभृताम्", "vigraha": "धर्मं बिभ्रति इति धर्मभृतः, तेषाम्", "type": "उपपद-तत्पुरुषः", "meaning": "Upholders of Dharma"},
                    {"pada": "अमृतोद्भवम्", "vigraha": "अमृतात् उद्भवः यस्य सः", "type": "बहुव्रीहिः", "meaning": "Born of / emerged with nectar"},
                    {"pada": "प्रकृतिभूतस्य", "vigraha": "प्रकृतिः भूतः (प्राप्तः), तस्य", "type": "सुप्-सुपा (विशेषण-विशेष्य)", "meaning": "Being in natural/healthy state"},
                    {"pada": "वदतां वर", "vigraha": "वदतां मध्ये वरः (श्रेष्ठः)", "type": "षष्ठी-निर्धारणम्", "meaning": "Foremost among orators/teachers"}
                ],
                "avyaya": [
                    {"pada": "च", "meaning": "समुच्चयार्थे (And)"},
                    {"pada": "उपसङ्गृह्य", "meaning": "क्त्वा-प्रत्ययान्त/ल्यबन्त अव्ययम् (Having touched respectfully)"}
                ],
                "shabdaroopa": [
                    {"pada": "सुश्रुतः", "pratipadika": "सुश्रुत", "linga": "पुंल्लिंगम्", "vibhakti": "प्रथमा", "vachana": "एकवचनम्", "karaka": "कर्ता"},
                    {"pada": "धन्वन्तरिम्", "pratipadika": "धन्वन्तरि", "linga": "पुंल्लिंगम्", "vibhakti": "द्वितीया", "vachana": "एकवचनम्", "karaka": "कर्म"},
                    {"pada": "चरणौ", "pratipadika": "चरण", "linga": "पुंल्लिंगम्", "vibhakti": "द्वितीया", "vachana": "द्विवचनम्", "karaka": "कर्म"},
                    {"pada": "वायोः", "pratipadika": "वायु", "linga": "पुंल्लिंगम्", "vibhakti": "षष्ठी", "vachana": "एकवचनम्", "karaka": "सम्बन्धः"},
                    {"pada": "कोपनैः", "pratipadika": "कोपन", "linga": "नपुंसकलिंगम्", "vibhakti": "तृतीया", "vachana": "बहुवचनम्", "karaka": "करणम् (हेतुः)"},
                    {"pada": "स्थानम्", "pratipadika": "स्थान", "linga": "नपुंसकलिंगम्", "vibhakti": "द्वितीया", "vachana": "एकवचनम्", "karaka": "कर्म"},
                    {"pada": "कर्म", "pratipadika": "कर्मन्", "linga": "नपुंसकलिंगम्", "vibhakti": "द्वितीया", "vachana": "एकवचनम्", "karaka": "कर्म"},
                    {"pada": "रोगान्", "pratipadika": "रोग", "linga": "पुंल्लिंगम्", "vibhakti": "द्वितीया", "vachana": "बहुवचनम्", "karaka": "कर्म"},
                    {"pada": "मे", "pratipadika": "अस्मद्", "linga": "त्रिषु", "vibhakti": "चतुर्थी", "vachana": "एकवचनम्", "karaka": "सम्प्रदानम्"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "परिपृच्छति", "dhatu": "प्रच्छ् (परि)", "gana": "तुदादि (६)", "meaning": "To inquire / ज्ञीप्सायाम्", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"},
                    {"kriyapada": "वद", "dhatu": "वद्", "gana": "भ्वादि (१)", "meaning": "To speak/instruct / व्यक्तायां वाचि", "lakara": "लोट्", "purusha": "मध्यमः", "vachana": "एकवचनम्"}
                ],
                "kridanta": [
                    {"pada": "वरिष्ठम्", "prakriti": "वृ", "pratyaya": "इष्ठन्", "type": "तद्धित", "meaning": "Most excellent / अतिशयेन श्रेष्ठः"},
                    {"pada": "उपसङ्गृह्य", "prakriti": "उप + सम् + ग्रह्", "pratyaya": "ल्यप्", "type": "कृत्", "meaning": "Having grasped/embraced reverently"},
                    {"pada": "व्यापन्नस्य", "prakriti": "वि + आ + पद्", "pratyaya": "क्त", "type": "कृत्", "meaning": "Vitiated / विकृतस्य"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_005_009",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 5,
            "shloka_number_display": "5-9",
            "text": "तस्य तद्वचनं श्रुत्वा प्राब्रवीद्भिषजां वरः |\nस्वयम्भूरेष भगवान् वायुरित्यभिशब्दितः ||५||\nस्वातन्त्र्यान्नित्यभावाच्च सर्वगत्वात्तथैव च |\nसर्वेषामेव सर्वात्मा सर्वलोकनमस्कृतः ||६||\nस्थित्युत्पत्तिविनाशेषु भूतानामेष कारणम् |\nअव्यक्तो व्यक्तकर्मा च रूक्षः शीतो लघुः खरः ||७||\nतिर्यग्गो द्विगुणश्चैव रजोबहुल एव च |\nअचिन्त्यवीर्यो दोषाणां नेता रोगसमूहराट् ||८||\nआशुकारी मुहुश्चारी पक्वाधानगुदालयः |९|",
            "transliteration": "tasya tadvacanaṁ śrutvā prābravīdbhiṣajāṁ varaḥ |\nsvayambhūreṣa bhagavān vāyurityabhiśabditaḥ ||5||\nsvātantryānnityabhāvācca sarvagatvāttathaiva ca |\nsarveṣāmeva sarvātmā sarvalokanamaskṛtaḥ ||6||\nsthityutpattivināśeṣu bhūtānāmeṣa kāraṇam |\navyakto vyaktakarmā ca rūkṣaḥ śīto laghuḥ kharaḥ ||7||\ntiryaggo dviguṇaścaiva rajobahula eva ca |\nacintyavīryo doṣāṇāṁ netā rogasamūharāṭ ||8||\nāśukārī muhuścārī pakvādhānagudālayaḥ |9|",
            "english_title": "Qualities, universal supremacy, divine attributes, and anatomical seat of Vāyu",
            "associated_pages": [7, 8, 9, 10, 11, 12],
            "padavibhaga": "तस्य | तत्-वचनम् | श्रुत्वा | प्राब्रवीत् | भिषजाम् | वरः | स्वयम्भूः | एष | भगवान् | वायुः | इति | अभिशब्दितः || स्वातन्त्र्यात् | नित्य-भावात् | च | सर्व-गत्वात् | तथा | एव | च | सर्वेषाम् | एव | सर्व-आत्मा | सर्व-लोक-नमस्कृतः || स्थिति-उत्पत्ति-विनाशेषु | भूतानाम् | एष | कारणम् | अव्यक्तः | व्यक्त-कर्मा | च | रूक्षः | शीतः | लघुः | खरः || तिर्यक्-गः | द्वि-गुणः | च | एव | रजः-बहुलः | एव | च | अचिन्त्य-वीर्यः | दोषाणाम् | नेता | रोग-समूह-राट् || आशु-कारी | मुहुः-चारी | पक्वाधान-गुद-आलयः ||",
            "anvaya": "तस्य (सुश्रुतस्य) तद्वचनं श्रुत्वा भिषजां वरः (धन्वन्तरिः) प्राब्रवीत्— एषः भगवान् वायुः 'स्वयम्भूः' इति अभिशब्दितः। स्वातन्त्र्यात्, नित्यभावात्, सर्वगत्वात् च (सः) सर्वेषाम् एव सर्वात्मा सर्वलोकनमसस्कृतः च अस्ति। एषः भूतानां स्थिति-उत्पत्ति-विनाशेषु कारणम् अस्ति। सः अव्यक्तः, व्यक्तकर्मा, रूक्षः, शीतः, लघुः, खरः, तिर्यग्गः, द्विगुणः, रजोबहुलः, अचिन्त्यवीर्यः, दोषाणां नेता, रोगसमूहराट्, आशुकारी, मुहुश्चारी, पक्वाधान-गुद-आलयः च अस्ति।",
            "shlokartha": "Hearing Suśruta's words, the best of physicians (Dhanvantari) replied: 'This divine Vāyu is known as Self-born (Svayambhū). Due to its independence, eternal nature, and omnipresence, it is the soul of all beings and is worshipped by all worlds. It is the cause of creation, sustenance, and destruction of all entities. It is unmanifest in form but manifest in action. Its attributes are dry, cold, light, rough. It moves obliquely, possesses two qualities (sound and touch), is predominantly Rajasic, possesses inconceivable potency, leads all doshas, rules over all disease groups, acts rapidly, moves repetitively, and resides primarily in the colon and rectum.'",
            "bhavartha": "अत्र भगवान् धन्वन्तरिः वायोः पारमार्थिकं व्यावहारिकं च स्वरूपं वर्णयति। वायुः न केवलं शरीरस्थः दोषः, अपितु सः 'स्वयम्भूः' ईश्वररूपः अस्ति। तस्य स्वातन्त्र्यं सर्वोपरि वर्तते, यतः विना वायुना किमपि चेष्टितुं न शक्यते। सः नित्यः अस्ति, सर्वव्यापकः च। सृष्टेः उत्पत्तिः, स्थितिः, प्रलयः च वायुना एव नियम्यते। यद्यपि वायुः इन्द्रियैः न दृश्यते (अव्यक्तः), तथापि तस्य कर्माणि (श्वास-प्रश्वास-गत्यादीनि) प्रत्यक्षाणि सन्ति। सः रजोगुणप्रधानः अस्ति, अतः एव क्रियाशीलः। आयुर्वेददृष्ट्या सः सर्वेषां दोषाणां चालकः (नेता) अस्ति।",
            "grammar_details": {
                "sandhi": [
                    {"pada": "प्राब्रवीद्भिषजाम्", "split": "प्राब्रवीत् + भिषजाम्", "type": "जश्त्वम्", "rule": "पदान्ते तकारस्य दकारः"},
                    {"pada": "वायुरित्यभिशब्दितः", "split": "वायुः + इति + अभिशब्दितः", "type": "रुत्वम्, यण्-सन्धिः", "rule": "विसर्गस्य रेफः, इ-कारस्य यकारः"},
                    {"pada": "स्वातन्त्र्यान्नित्यभावात्", "split": "स्वातन्त्र्यात् + नित्यभावात्", "type": "अनुनासिकः", "rule": "तकारस्य नकारे परिवर्तनम्"},
                    {"pada": "तथैव", "split": "तथा + एव", "type": "वृद्धिः", "rule": "आ + ए = ऐ"},
                    {"pada": "स्थित्युत्पत्ति", "split": "स्थिति + उत्पत्ति", "type": "यण्-सन्धिः", "rule": "इ-कारस्य यकारः"},
                    {"pada": "द्विगुणश्चैव", "split": "द्विगुणः + च + एव", "type": "सत्वम्, वृद्धिः", "rule": "विसर्गस्य सः, अ + ए = ऐ"}
                ],
                "samasa": [
                    {"pada": "तद्वचनम्", "vigraha": "तस्य वचनम्", "type": "षष्ठी-तत्पुरुषः", "meaning": "His words"},
                    {"pada": "सर्वगत्वात्", "vigraha": "सर्वं गच्छति इति सर्वगः, तस्य भावः", "type": "उपपद-तत्पुरुषः + तल्", "meaning": "Because of omnipresence"},
                    {"pada": "सर्वात्मा", "vigraha": "सर्वेषाम् आत्मा", "type": "षष्ठी-तत्पुरुषः", "meaning": "Soul/life of all"},
                    {"pada": "व्यक्तकर्मा", "vigraha": "व्यक्तं कर्म यस्य सः", "type": "बहुव्रीहिः", "meaning": "Whose actions are manifested"},
                    {"pada": "अचिन्त्यवीर्यः", "vigraha": "अचिन्त्यं वीर्यं यस्य सः", "type": "बहुव्रीहिः", "meaning": "Possessing inconceivable power"},
                    {"pada": "रोगसमूहराट्", "vigraha": "रोगाणां समूहः, तस्मिन् राजते इति", "type": "षष्ठी-तत्पुरुषः + उपपद", "meaning": "King/master over all diseases"},
                    {"pada": "पक्वाधानगुदालयः", "vigraha": "पक्वाधानं च गुदं च तौ आलयः यस्य सः", "type": "बहुव्रीहिः", "meaning": "Residing in the colon and rectum"}
                ],
                "avyaya": [
                    {"pada": "इति", "meaning": "स्वरूप-बोधकम् (Thus)"},
                    {"pada": "च", "meaning": "समुच्चयार्थे (And)"},
                    {"pada": "एव", "meaning": "अवधारणार्थे (Indeed / Only)"},
                    {"pada": "तथा", "meaning": "उपमा/समुच्चयार्थे (Similarly)"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "प्राब्रवीत्", "dhatu": "प्र + ब्रू", "gana": "अदादि (२)", "meaning": "Spoke / व्यक्तायां वाचि", "lakara": "लङ्", "purusha": "प्रथमः", "vachana": "एकवचनम्"}
                ],
                "kridanta": [
                    {"pada": "श्रुत्वा", "prakriti": "श्रु", "pratyaya": "क्त्वा", "type": "कृत्", "meaning": "Having heard / आकर्ण्य"},
                    {"pada": "स्वयम्भूः", "prakriti": "स्वयम् + भू", "pratyaya": "क्विप्", "type": "कृत्", "meaning": "Self-born / स्वतः जातः"},
                    {"pada": "आशुकारी", "prakriti": "आशु + कृ", "pratyaya": "णिनि", "type": "कृत्", "meaning": "Fast-acting / शीघ्रं करोति यः"},
                    {"pada": "मुहुश्चारी", "prakriti": "मुहुः + चर्", "pratyaya": "णिनि", "type": "कृत्", "meaning": "Moving repeatedly / पुनः पुनः चरति यः"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_009_010",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 9,
            "shloka_number_display": "9-10",
            "text": "देहे विचरतस्तस्य लक्षणानि निबोध मे ||९||\nदोषधात्वग्निसमतां सम्प्राप्तिं विषयेषु च |\nक्रियाणामानुलोम्यं च करोत्यकुपितोऽनिलः ||१०||",
            "transliteration": "dehe vicaratastasya lakṣaṇāni nibodha me ||9||\ndoṣadhātvagnisamatāṁ samprāptiṁ viṣayeṣu ca |\nkriyāṇāmānulomyaṁ ca karotyakupito'nilaḥ ||10||",
            "english_title": "Physiological actions of normal/unvitiated Vāyu in the body",
            "associated_pages": [12, 13, 14, 15, 16],
            "padavibhaga": "देहे | विचरतः | तस्य | लक्षणानि | निबोध | मे || दोष-धातु-अग्नि-समताम् | सम्प्राप्तिम् | विषयेषु | च | क्रियाणाम् | आनुलोम्यम् | च | करोति | अकुपितः | अनिलः ||",
            "anvaya": "देहे विचरतः तस्य (वायोः) लक्षणानि मे (मत्तः) निबोध। अकुपितः अनिलः दोष-धातु-अग्नि-समतां विषयेषु सम्प्राप्तिं क्रियाणाम् आनुलोम्यं च करोति।",
            "shlokartha": "Listen from me to the characteristics of Vāyu as it circulates within the body. When Vāyu is in its non-vitiated (normal) state, it maintains the equilibrium of the Doshas, Dhatus, and Agni (digestive fire). It facilitates the proper perception of sensory objects by the senses and ensures the natural, downward, and unobstructed movement (Anulomya) of all bodily functions.",
            "bhavartha": "अस्मिन् श्लोके भगवान् धन्वन्तरिः स्वस्थशरीरे वायोः कर्माणि वर्णयति। यदा वायुः अकुपितः (Normal state) भवति, तदा सः शरीरस्य धारकः भवति। सः शरीरस्थानां त्रयाणां स्तम्भानां — दोषाणां, धातूनां, अग्नीनां च साम्यं रक्षति। यदि वायुः सम्यक् वर्तते, तर्हि इन्द्रियाणि स्वविषयान् सुखेन गृह्णन्ति। अपि च, शरीरस्य सर्वाः क्रियाः (मल-मूत्र-उत्सर्गादयः, रक्तसञ्चारादयश्च) 'आनुलोम्येन' अर्थात् स्वाभाविकानुगत्या सम्यक् प्रचलन्ति।",
            "grammar_details": {
                "sandhi": [
                    {"pada": "विचरतस्तस्य", "split": "विचरतः + तस्य", "type": "विसर्ग-सत्वम्", "rule": "खरि परे विसर्गस्य सकारः"},
                    {"pada": "करोत्यकुपितोऽनिलः", "split": "करोति + अकुपितः + अनिलः", "type": "यण्, उत्व, पूर्वरूप", "rule": "इ -> य्, विसर्ग -> ओ, अ -> ऽ"},
                    {"pada": "दोषधात्वग्न्यवैकृतम्", "split": "दोष-धातु-अग्नि + अवैकृतम्", "type": "यण्-सन्धिः", "rule": "इ-कारस्य यकारः"}
                ],
                "samasa": [
                    {"pada": "दोषधात्वग्निसमताम्", "vigraha": "दोषाश्च धातवश्च अग्नयश्च (इतरेतर द्वन्द्वः), तेषां समता (षष्ठी तत्पुरुषः)", "type": "द्वन्द्व-गर्भ-तत्पुरुषः", "meaning": "Equilibrium of doshas, dhatus, and digestive fire"},
                    {"pada": "अकुपितः", "vigraha": "न कुपितः", "type": "नञ्-तत्पुरुषः", "meaning": "Unvitiated, balanced"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "निबोध", "dhatu": "नि + बुध्", "gana": "दिवादि (४)", "meaning": "Understand / Listen / अवगमने", "lakara": "लोट्", "purusha": "मध्यमः", "vachana": "एकवचनम्"},
                    {"kriyapada": "करोति", "dhatu": "कृ", "gana": "तनादि (८)", "meaning": "Performs / करणे", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_011",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 11,
            "shloka_number_display": "11",
            "text": "यथाऽग्निः पञ्चधा भिन्नो नामस्थानक्रियामयैः |\nभिन्नोऽनिलस्तथा ह्येको नामस्थानक्रियामयैः ||११||",
            "transliteration": "yathā'gniḥ pañcadhā bhinno nāmasthānakriyāmayaiḥ |\nbhinno'nilastathā hyeko nāmasthānakriyāmayaiḥ ||11||",
            "english_title": "Five-fold classification of Vāyu analogous to Agni/Pitta",
            "associated_pages": [16, 17, 18, 19],
            "padavibhaga": "यथा | अग्निः | पञ्चधा | भिन्नः | नाम-स्थान-क्रिया-मयैः | भिन्नः | अनिलः | तथा | हि | एकः | नाम-स्थान-क्रिया-मयैः ||",
            "anvaya": "यथा अग्निः नाम-स्थान-क्रिया-मयैः पञ्चधा भिन्नः (भवति), तथा हि एकः अनिलः (अपि) नाम-स्थान-क्रिया-मयैः भिन्नः (भवति)।",
            "shlokartha": "Just as Agni (Pitta/Fire) is divided into five types based on its name, location, function, and the diseases it causes, similarly, the single Vāyu (Anila) is also categorized into five types based on its name, location, function, and specific disorder.",
            "bhavartha": "अत्र आयुर्वेदस्य सिद्धान्तः उपस्थापितः। यद्यपि शरीरे वायुः एकः एव मूलतत्त्वरूपेण वर्तते, तथापि तस्य कार्यक्षेत्राणि भिन्नानि सन्ति। यथा पित्तम् (अग्निः) पाचक-रञ्जक-साधक-आलोचक-भ्राजक-भेदेन पञ्चविधं भवति, तथैव वायुः अपि प्राण-उदान-समान-व्यान-अपान-भेदेन पञ्चधा विभज्यते। एषः भेदः चतुर्भिः आधारैः क्रियते— १. नाम (प्राणादयः), २. स्थान (हृदय-नाभ्यादयः), ३. क्रिया (श्वास-प्रश्वास-मलाद्युत्सर्गादयः), ४. आमय (तत्तत्स्थानगताः विशेषाः रोगाः)। एतेन वैद्यानां चिकित्सा-सौकर्यं भवति।",
            "grammar_details": {
                "samasa": [
                    {"pada": "नामस्थानक्रियामयैः", "vigraha": "नाम च स्थानं च क्रिया च आमयश्च (इतरेतर द्वन्द्वः), तैः", "type": "द्वन्द्व-समासः", "meaning": "By name, location, function, and disease"}
                ],
                "avyaya": [
                    {"pada": "यथा", "meaning": "उपमार्थे (Just as)"},
                    {"pada": "तथा", "meaning": "उपमार्थे (Similarly)"},
                    {"pada": "हि", "meaning": "हेतु-प्रसिद्धौ (Indeed / Because)"},
                    {"pada": "पञ्चधा", "meaning": "प्रकार-वाचक-तद्धितान्त-अव्ययम् (In five ways)"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_012",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 12,
            "shloka_number_display": "12",
            "text": "प्राणोदानौ समानश्च व्यानश्चापान एव च |\nस्थानस्था मारुताः पञ्च यापयन्ति शरीरिणम् ||१२||",
            "transliteration": "prāṇodānau samānaśca vyānaścāpāna eva ca |\nsthānasthā mārutāḥ pañca yāpayanti śarīriṇam ||12||",
            "english_title": "The five subtypes of Vayu and their collective role in sustaining bodily life",
            "associated_pages": [19, 20, 21, 22],
            "padavibhaga": "प्राण-उदानौ | समानः | च | व्यानः | च | अपानः | एव | च | स्थान-स्थाः | मारुताः | पञ्च | यापयन्ति | शरीरिणम् ||",
            "anvaya": "प्राणोदानौ समानः व्यानः च अपानः च एव (इति) एते पञ्च स्थानस्थाः मारुताः शरीरिणं यापयन्ति।",
            "shlokartha": "Prāṇa, Udāna, Samāna, Vyāna, and Apāna—these five types of Vāyu, remaining in their respective locations, sustain and maintain the living being (the embodied soul).",
            "bhavartha": "अस्मिन् श्लोके वायोः पञ्चभेदाः तेषां मुख्यं प्रयोजनं च वर्णितम्। यद्यपि वायुः एकः एव, तथापि शरीरे कार्याणां भेदेन सः पञ्चधा विभक्तः — प्राणः, उदानः, समानः, व्यानः, अपानः च। एते पञ्चापि वायवः यदा स्वस्वस्थानेषु प्राकृतरूपेण तिष्ठन्ति, तदा एव शरीरस्य जीवनयात्रा सम्यक् प्रचलति। एतेषां सामञ्जस्येन एव मनुष्यः जीवति। अतः एते 'शरीरधारकाः' सन्ति।",
            "grammar_details": {
                "samasa": [
                    {"pada": "प्राणोदानौ", "vigraha": "प्राणश्च उदानश्च", "type": "इतरेतर-द्वन्द्वः", "meaning": "Prana and Udana"},
                    {"pada": "स्थानस्थाः", "vigraha": "स्थाने तिष्ठन्ति इति", "type": "उपपद-तत्पुरुषः", "meaning": "Situated in their respective anatomical sites"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "यापयन्ति", "dhatu": "या (णिच्)", "gana": "अदादि (२)", "meaning": "To sustain / maintain / प्रापणे धारणे", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "बहुवचनम्"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_013_014",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 13,
            "shloka_number_display": "13-14",
            "text": "यो वायुर्वक्त्रसञ्चारी स प्राणो नाम देहधृक् |\nसोऽन्नं प्रवेशयत्यन्तः प्राणांश्चाप्यवलम्बते ||१३||\nप्रायशः कुरुते दुष्टो हिक्काश्वासादिकान् गदान् |१४|",
            "transliteration": "yo vāyurvaktrasañcārī sa prāṇo nāma dehadhṛk |\nso'nnaṁ praveśayatyantaḥ prāṇāṁścāpyavalambate ||13||\nprāyaśaḥ kurute duṣṭo hikkāśvāsādikān gadān |14|",
            "english_title": "Location, normal function, and vitiation pathology of Prāṇa Vāyu",
            "associated_pages": [22, 23, 24, 25, 26],
            "padavibhaga": "यः | वायुः | वक्त्र-सञ्चारी | सः | प्राणः | नाम | देह-धृक् || सः | अन्नम् | प्रवेशयति | अन्तः | प्राणान् | च | अपि | अवलम्बते || प्रायशः | कुरुते | दुष्टः | हिक्का-श्वास-आदिकान् | गदान् ||",
            "anvaya": "यः वायुः वक्त्रसञ्चारी (अस्ति), सः देहधृक् 'प्राणः' नाम (अस्ति)। सः अन्नम् अन्तः प्रवेशयति, प्राणान् च अपि अवलम्बते। दुष्टः (सः) प्रायशः हिक्का-श्वास-आदिकान् गदान् कुरुते।",
            "shlokartha": "The Vāyu that circulates in the mouth (and throat) is called 'Prāṇa'; it is the sustainer of the body. It propels food into the interior (stomach) and supports the vital life-breaths. When this Vāyu becomes vitiated, it generally causes diseases such as hiccups, asthma, and other respiratory disorders.",
            "bhavartha": "अत्र पञ्चविधवायूनां मध्ये प्रथमस्य 'प्राणवायोः' स्वरूपं कार्यं च निरूपितम्। प्राणवायुः मुख्यतया मुखे कण्ठे च विचरति, अतः अस्य 'वक्त्रसञ्चारी' इति संज्ञा। अस्य द्वे मुख्ये कार्ये स्तः — प्रथमं तु बहिः स्थितस्य आहारस्य अन्तः (जठरं प्रति) नयनम्, द्वितीयं च इन्द्रियाणां मनसश्च धारणम् (प्राणावलम्बनम्)। यतो हि एषः जीवनस्य आधारः, अतः 'देहधृक्' इत्युच्यते। यदा अयं वायुः मिथ्याहारादिना विकृतः (दुष्टः) भवति, तदा सः ऊर्ध्वगामी भूत्वा हिक्का (Hiccup), श्वासः (Asthma/Dyspnea) इत्यादीन् प्राणघातकान् व्याधीन् जनयति।",
            "grammar_details": {
                "samasa": [
                    {"pada": "वक्त्रसञ्चारी", "vigraha": "वक्त्रे सञ्चरति इति", "type": "उपपद-तत्पुरुषः", "meaning": "Circulating in mouth/oral cavity"},
                    {"pada": "देहधृक्", "vigraha": "देहं धरति इति", "type": "उपपद-तत्पुरुषः", "meaning": "Sustainer of body"},
                    {"pada": "हिक्काश्वासादिकान्", "vigraha": "हिक्का च श्वासश्च तौ आदिः येषां ते, तान्", "type": "बहुव्रीहिः", "meaning": "Disorders starting with hiccups and asthma"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "प्रवेशयति", "dhatu": "प्र + विश् (णिच्)", "gana": "तुदादि (६)", "meaning": "To cause to enter / प्रवेशने", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"},
                    {"kriyapada": "अवलम्बते", "dhatu": "अव + लम्ब्", "gana": "भ्वादि (१)", "meaning": "To support / आश्रये", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_014_015",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 14,
            "shloka_number_display": "14-15",
            "text": "उदानो नाम यस्तूर्ध्वमुपैति पवनोत्तमः ||१४||\nतेन भाषितगीतादिविशेषोऽभिप्रवर्तते |\nऊर्ध्वजत्रुगतान् रोगान् करोति च विशेषतः ||१५||",
            "transliteration": "udāno nāma yastūrdhvamupaiti pavanottamaḥ ||14||\ntena bhāṣitagītādiviśeṣo'bhipravartate |\nūrdhvajatrugatān rogān karoti ca viśeṣataḥ ||15||",
            "english_title": "Location, functions, and pathology of Udāna Vāyu",
            "associated_pages": [27, 28, 29, 30],
            "padavibhaga": "उदानः | नाम | यः | तु | ऊर्ध्वम् | उपैति | पवन-उत्तमः | तेन | भाषित-गीत-आदि-विशेषः | अभिप्रवर्तते | ऊर्ध्व-जत्रु-गतान् | रोगान् | करोति | च | विशेषतः ||",
            "anvaya": "यः पवनोत्तमः उदानः नाम तु ऊर्ध्वम् उपैति, तेन भाषित-गीत-आदि-विशेषः अभिप्रवर्तते। (सः) विशेषतः ऊर्ध्वजत्रुगतान् रोगान् च करोति।",
            "shlokartha": "The 'Udāna' Vāyu, the best among winds, moves upwards (towards the throat and head). It is responsible for the specific functions of speech, singing, and vocal expression. When vitiated, it particularly causes diseases in the organs located above the clavicle (the supraclavicular region).",
            "bhavartha": "अत्र उदानवायोः स्वरूपं कार्यं च प्रतिपादितम्। उदानवायुः उरःस्थाने (वक्षसि) स्थित्वा कण्ठं शिरश्च प्रति ऊर्ध्वगामी भवति, अतः अस्य 'पवनोत्तमः' इति संज्ञा। अस्य मुख्यं कार्यं वाक्प्रवृत्तिः अस्ति। मनुष्यस्य भाषणं, गायनं, शब्दोच्चारणं च उदानवायुना एव सम्भवति। यदा अयं वायुः कुपितः भवति, तदा सः जत्रुतः (Clavicle) ऊर्ध्वं स्थितेषु अङ्गेषु — यथा नेत्र-कर्ण-नासिका-मुख-शिरःसु — विविधान् व्याधीन् जनयति।",
            "grammar_details": {
                "samasa": [
                    {"pada": "पवनोत्तमः", "vigraha": "पवनानाम् उत्तमः", "type": "षष्ठी-तत्पुरुषः", "meaning": "Foremost among bodily winds"},
                    {"pada": "ऊर्ध्वजत्रुगतान्", "vigraha": "ऊर्ध्वं जत्रु (कर्मधारयः), तत्र गताः (सप्तमी तत्पुरुषः), तान्", "type": "तत्पुरुषः", "meaning": "Located above the clavicle / supraclavicular"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "उपैति", "dhatu": "उप + इ", "gana": "अदादि (२)", "meaning": "Moves towards / गत्यर्थे", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"},
                    {"kriyapada": "अभिप्रवर्तते", "dhatu": "अभि + प्र + वृत्", "gana": "भ्वादि (१)", "meaning": "Proceeds / functions / वर्तने", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"}
                ]
            }
        },
        {
            "id": "sushruta_nidana_ch1_shloka_016_017",
            "source": "Sushruta Samhita",
            "sthana": "Nidana Sthana",
            "chapter": "Vatavyadhi Nidana",
            "chapter_number": 1,
            "shloka_number": 16,
            "shloka_number_display": "16-17",
            "text": "आमपक्वाशयचरः समानो वह्निंसङ्गतः |\nसोऽन्नं पचति तज्जांश्च विशेषांविनिविनक्ति हि ||१६||\nगुल्माग्निसादातीसारप्रभृतीन् कुरुते गदान् |१७|",
            "transliteration": "āmapakvāśayacaraḥ samāno vahniṁsaṅgataḥ |\nso'nnaṁ pacati tajjāṁśca viśeṣāṁvinivinakti hi ||16||\ngulmāgnisādātīsāraprabhṛtīn kurute gadān |17|",
            "english_title": "Location, digestive action, and digestive disorders of Samāna Vāyu",
            "associated_pages": [30, 31, 32, 33, 34],
            "padavibhaga": "आम-पक्वाशय-चरः | समानः | वह्नि-सङ्गतः | सः | अन्नम् | पचति | तत्-जान् | च | विशेषान् | विनिविनक्ति | हि | गुल्म-अग्निसाद-अतीसार-प्रभृतीन् | कुरुते | गदान् ||",
            "anvaya": "आम-पक्वाशय-चरः वह्निंसङ्गतः समानः (वायुः) अन्नं पचति, तज्जान् विशेषान् च हि विनिविनक्ति। (सः विकृतः सन्) गुल्म-अग्निसाद-अतीसार-प्रभृतीन् गदान् कुरुते।",
            "shlokartha": "The 'Samāna' Vāyu, which moves between the stomach (Āmāśaya) and the intestines (Pakvāśaya) and is associated with the digestive fire (Agni), digests the food and separates the products of digestion (into essence/nutrients and waste). When vitiated, it causes diseases such as abdominal tumors (Gulma), loss of digestive power (Agnisāda), and diarrhea (Atisāra).",
            "bhavartha": "अत्र समानवायोः स्थानं कार्यं च निरूपितम्। समानवायुः आमाशयस्य पक्वाशयस्य च मध्ये (अर्थात् क्षुद्रान्त्रे) विचरति। अस्य मुख्यं वैशिष्ट्यं 'वह्निंसङ्गत्वम्' अस्ति; एषः पाचकपित्तेन (अग्निना) सह मिलित्वा कार्यं करोति। अस्य द्वे मुख्ये कार्ये स्तः — प्रथमं भोजनस्य पाचनम्, द्वितीयं च पाचितस्य अन्नस्य 'सार' (Nutrients) तथा 'किट्ट' (Waste) इति भागद्वये पृथक्करणम्। यदा अयं वायुः कुपितः भवति, तदा पाचनप्रक्रिया विकृता भवति, येन गुल्मः, अग्निमान्द्यम्, अतीसारः इत्यादयः जठर-सम्बन्धिनः व्याधयः जायन्ते।",
            "grammar_details": {
                "samasa": [
                    {"pada": "आमपक्वाशयचरः", "vigraha": "आमश्च पक्वाशयश्च (द्वन्द्वः), तयोः चरति इति (उपपदः)", "type": "द्वन्द्व-गर्भ-उपपद-तत्पुरुषः", "meaning": "Moving between stomach and colon"},
                    {"pada": "वह्निंसङ्गतः", "vigraha": "वह्निना सङ्गतः", "type": "तृतीया-तत्पुरुषः", "meaning": "United / associated with digestive fire"},
                    {"pada": "गुल्माग्निसादातीसारप्रभृतीन्", "vigraha": "गुल्मश्च अग्निसादश्च अतीसारश्च (द्वन्द्वः), ते प्रभृतयः येषां ते (बहुव्रीहिः), तान्", "type": "बहुव्रीहिः", "meaning": "Disorders starting with Gulma, loss of digestion, diarrhea"}
                ],
                "dhaturoopa": [
                    {"kriyapada": "पचति", "dhatu": "पच्", "gana": "भ्वादि (१)", "meaning": "To digest / cook / पाके", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"},
                    {"kriyapada": "विनिविनक्ति", "dhatu": "वि + नि + विच्", "gana": "रुधादि (७)", "meaning": "To separate / isolate / पृथग्भावे", "lakara": "लट्", "purusha": "प्रथमः", "vachana": "एकवचनम्"}
                ]
            }
        }
    ]


def get_curated_methodology_chunks() -> List[Dict[str, Any]]:
    """
    Extracts the structured 7-step Ayurvidya/Prabhashanam principles from 'steps of Ayurvidya.pdf'.
    Used as high-relevance methodology knowledge in RAG retrieval.
    """
    return [
        {
            "id": "methodology_sampradaanam",
            "content_type": "methodology",
            "category": "step1_sampradaanam",
            "title": "Sampradaanam Technique - Proper Metrical Division",
            "text": (
                "Step 1: संप्रदानम् (Sampradaanam) - 'सम्यक् प्रविभज्य दानम्' - skillful offering by dividing "
                "thoughtfully according to the capacity of the student. Sushruta Samhita Sutrasthana Ch 3 "
                "(अध्यायनसम्प्रदानीयम्). In padyasutra (shloka in Anushtup chhandas), each 16-syllable metrical "
                "line (ardhashloka) contains two 8-syllable padas. A 2-line shloka has 4 padas, a 3-line passage "
                "has 6 padas, and a 4-line passage has 8 padas. Step 1 divides the shloka strictly into its actual "
                "metrical padas (each 8 syllables in Anushtup meter), performing sandhi-vichchheda for ease of chanting."
            ),
            "metadata": {"step": 1, "source": "steps of Ayurvidya.pdf", "topic": "Sampradaanam"}
        },
        {
            "id": "methodology_padavibhaga",
            "content_type": "methodology",
            "category": "step2_padavibhaga",
            "title": "Padavibhaga Rules - Sanskrit Pada Classification",
            "text": (
                "Step 2: पदविभागः (Padavibhaga) - Identification, separation, and analysis of padas. "
                "Rules: 1. Three types of pada: Subanta (नामपद - noun/pronoun with vibhakti & vachana), "
                "Tinganta (क्रियापद - verb with lakara, purusha, vachana), Avyaya (indeclinable). "
                "2. Sandhivibhajana: If sandhi is BETWEEN two separate padas, split them. "
                "3. Sandhi within a single pada must NOT be split. "
                "4. Samastapada: A compound word (samasa) must be treated as ONE pada and NEVER split."
            ),
            "metadata": {"step": 2, "source": "steps of Ayurvidya.pdf", "topic": "Padavibhaga"}
        },
        {
            "id": "methodology_anwaya",
            "content_type": "methodology",
            "category": "step3_anwaya",
            "title": "Arthanwaya Rules - Grammatical Meaning Flow",
            "text": (
                "Step 3: अन्वयः / अर्थान्वयः (Anwaya) - 'अर्थम् अनुसृत्य कृतः अर्थान्वयः'. "
                "Rules in sequence: Level 1: Kartru (Prathama vibhakti) -> Karma (Dwitiya vibhakti) -> Kriya (Verb at end). "
                "Level 2: Visheshana (adjective) placed immediately before its Visheshya (noun). "
                "Level 3: Tritiya vibhakti = Karana (instrument) or Hetu (reason) placed near kriya. "
                "Level 4: Words विना, समम्, सह, युक्तम्, जातम् form one unit with adjoining Tritiya pada. "
                "Level 5: Chaturthi vibhakti = Recipient or purpose; placed before नमः/नमस्कारः or near kriya. "
                "Level 6: Panchami vibhakti = Hetu or Apadana (separation). Precedes words like रक्षः, भीतिः, भयः, जातः, मुक्तः, ऋते. "
                "तसिल् (तः-ending words like विशेषतः, वाततः) treated as Panchami. "
                "Level 7: Shashti vibhakti = relation/connection, placed before the noun it qualifies and before मध्ये. "
                "Level 8: Saptami vibhakti = Adhishthana (place), Kala (time), or Sati-saptami (condition)."
            ),
            "metadata": {"step": 3, "source": "steps of Ayurvidya.pdf", "topic": "Anwaya"}
        },
        {
            "id": "methodology_anwayartha",
            "content_type": "methodology",
            "category": "step4_anwayartha",
            "title": "Anwayartha - Direct Literal Word-by-Word Meaning",
            "text": (
                "Step 4: अन्वयार्थः (Anwayartha) - Direct, literal, phrase-by-phrase meaning strictly "
                "following the Anwaya order (Kartru -> Karma -> Kriya). Every pada must be accounted for "
                "without skipping. No interpretation, personal commentary, or contextual extrapolation."
            ),
            "metadata": {"step": 4, "source": "steps of Ayurvidya.pdf", "topic": "Anwayartha"}
        },
        {
            "id": "methodology_bhavartha",
            "content_type": "methodology",
            "category": "step5_bhavartha",
            "title": "Bhavartha - Contextual Purport and Acharya's Intent",
            "text": (
                "Step 5: भावार्थः / भावानुवादः (Bhavartha) - 'सत्तां (सूत्राणि) अनुसृत्य वादः भावानुवादः'. "
                "A concise summary (2-5 sentences) of the Acharya's true intended meaning (Bhaava). "
                "Anchored in the context of the prakarana (topic), adhyaya (chapter), sthaana, and tantra. "
                "Must represent the author's intention, not personal subjective commentary."
            ),
            "metadata": {"step": 5, "source": "steps of Ayurvidya.pdf", "topic": "Bhavartha"}
        },
        {
            "id": "methodology_padakrutyam",
            "content_type": "methodology",
            "category": "step6_padakrutyam",
            "title": "Padakrutyam - Morphological and Lexical Formation Analysis",
            "text": (
                "Step 6: पदकृत्यम् (Padakrutyam) - Journey and samskaras in understanding the formation of a word. "
                "For significant padas: 1. Synonyms (from Amarakosha). 2. Subanta (linga, vibhakti, vachana). "
                "3. Tinganta (lakara, purusha, vachana). 4. Avyaya type. 5. Samastapada (vigrahavakya, samasa type). "
                "6. Dhatu & Dhatvartha (from Dhatu Ratnavali / Bruhat-dhatu-kusumakara). "
                "7. Upasarga and its role. 8. Contribution to the unique holistic meaning of the sutra."
            ),
            "metadata": {"step": 6, "source": "steps of Ayurvidya.pdf", "topic": "Padakrutyam"}
        },
        {
            "id": "methodology_dhvanitartha",
            "content_type": "methodology",
            "category": "step7_dhvanitartha",
            "title": "Dhvanitartha - Unstated Implied Deeper Meaning",
            "text": (
                "Step 7: ध्वनितार्थः (Dhvanitartha) - Unravelling the unstated, deeper intent of the Acharya "
                "between the lines. Requires: 1. Vyakarana rules. 2. Tantrayukti (classical compositional tools). "
                "3. Tantra Samanvaya (comparative synthesis across Charaka, Sushruta, Ashtanga Hridaya). "
                "Must provide 2-4 sentences revealing what the Acharya uniquely hints at."
            ),
            "metadata": {"step": 7, "source": "steps of Ayurvidya.pdf", "topic": "Dhvanitartha"}
        }
    ]
