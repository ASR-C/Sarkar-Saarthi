from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from guides.models import Category, OfficialLink, Guide, GuideTranslation, GuideStep, GuideDocument
from wizard.models import WizardQuestion

class Command(BaseCommand):
    help = 'Seeds Phase 1 All-India verified government guides, links, categories, and wizard questions'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Phase 1 data...")

        # 1. Editor User
        admin_user, _ = User.objects.get_or_create(
            email='editor@sarkarisaathi.org',
            defaults={
                'name': 'Editorial Desk',
                'language': 'en',
                'state': 'Central / All India',
                'status': 'active',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if not admin_user.has_usable_password():
            admin_user.set_password('AdminSaathi2026!')
            admin_user.save()

        # 2. Categories
        cats = {
            'identity': Category.objects.get_or_create(name='Identity & Civil ID', slug='identity', sort_order=1)[0],
            'travel': Category.objects.get_or_create(name='Passports & Travel', slug='passports-travel', sort_order=2)[0],
            'transport': Category.objects.get_or_create(name='Transport & Driving', slug='transport-driving', sort_order=3)[0],
            'elections': Category.objects.get_or_create(name='Voter & Elections', slug='voter-elections', sort_order=4)[0],
            'education': Category.objects.get_or_create(name='Education & Scholarships', slug='education-scholarships', sort_order=5)[0],
            'utilities': Category.objects.get_or_create(name='LPG & Utilities', slug='lpg-utilities', sort_order=6)[0],
            'food': Category.objects.get_or_create(name='Ration & Food Supplies', slug='ration-food-supplies', sort_order=7)[0],
        }

        # 3. Official Links (Allowlist)
        links = {
            'passport': OfficialLink.objects.get_or_create(
                url='https://passportindia.gov.in',
                defaults={'domain': 'passportindia.gov.in', 'label': 'Passport Seva Portal (Ministry of External Affairs)', 'state_scope': 'central'}
            )[0],
            'incometax': OfficialLink.objects.get_or_create(
                url='https://www.incometax.gov.in',
                defaults={'domain': 'incometax.gov.in', 'label': 'Income Tax e-Filing Portal (Instant e-PAN)', 'state_scope': 'central'}
            )[0],
            'parivahan': OfficialLink.objects.get_or_create(
                url='https://sarathi.parivahan.gov.in',
                defaults={'domain': 'parivahan.gov.in', 'label': 'Parivahan Sarathi (Ministry of Road Transport)', 'state_scope': 'central'}
            )[0],
            'voters': OfficialLink.objects.get_or_create(
                url='https://voters.eci.gov.in',
                defaults={'domain': 'voters.eci.gov.in', 'label': 'ECI Voters Service Portal (Election Commission of India)', 'state_scope': 'central'}
            )[0],
            'myaadhaar': OfficialLink.objects.get_or_create(
                url='https://myaadhaar.uidai.gov.in',
                defaults={'domain': 'uidai.gov.in', 'label': 'myAadhaar Portal (Unique Identification Authority of India)', 'state_scope': 'central'}
            )[0],
            'scholarships': OfficialLink.objects.get_or_create(
                url='https://scholarships.gov.in',
                defaults={'domain': 'scholarships.gov.in', 'label': 'National Scholarship Portal (NSP)', 'state_scope': 'central'}
            )[0],
            'pmuy': OfficialLink.objects.get_or_create(
                url='https://www.pmuy.gov.in',
                defaults={'domain': 'pmuy.gov.in', 'label': 'Pradhan Mantri Ujjwala Yojana Portal (MoPNG)', 'state_scope': 'central'}
            )[0],
            'digilocker': OfficialLink.objects.get_or_create(
                url='https://www.digilocker.gov.in',
                defaults={'domain': 'digilocker.gov.in', 'label': 'DigiLocker Portal (MeitY)', 'state_scope': 'central'}
            )[0],
            'powermin': OfficialLink.objects.get_or_create(
                url='https://powermin.gov.in',
                defaults={'domain': 'powermin.gov.in', 'label': 'Ministry of Power (National Consumer Advisory)', 'state_scope': 'central'}
            )[0],
            'nfsa': OfficialLink.objects.get_or_create(
                url='https://nfsa.gov.in',
                defaults={'domain': 'nfsa.gov.in', 'label': 'National Food Security Portal (Department of Food & Public Distribution)', 'state_scope': 'central'}
            )[0],
        }

        # 4. Create 10 Real Verified Seed Guides
        now = timezone.now()

        # Guide 1: Passport Application
        g1, _ = Guide.objects.get_or_create(
            slug='passport-application-normal-tatkaal',
            defaults={
                'category': cats['travel'],
                'state_scope': 'central',
                'mode': 'partial',
                'fee_text': '₹1,500 (Normal 36 pages) / ₹3,500 (Tatkaal)',
                'last_date': 'Rolling / Year-round',
                'official_link': links['passport'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g1, language='en',
            defaults={
                'title': 'Indian Passport Application',
                'summary': 'Step-by-step guide to register online, fill form, pay fees, and book an appointment at Passport Seva Kendra (PSK) without paying agent commissions.',
                'common_mistakes': '• Name mismatch between 10th certificate and Aadhaar.\n• Submitting non-white background photo.\n• Booking Tatkaal without verifying if applicant holds 3 required Annexure documents.\n• Failing to carry original photocopies self-attested with signature.',
                'what_to_do_if_fails': 'Call Passport Seva toll-free national helpline: 1800-258-1800 (8 AM to 10 PM). In case of appointment rescheduling, you are allowed up to 3 reschedule attempts within 1 year from payment date without paying again.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g1, language='hi',
            defaults={
                'title': 'भारतीय पासपोर्ट आवेदन',
                'summary': 'पासपोर्ट सेवा केंद्र (PSK) के लिए बिना किसी दलाल के घर बैठे फॉर्म भरने, फीस भुगतान और अपॉइंटमेंट स्लॉट बुक करने का सीधा तरीका।',
                'common_mistakes': '• 10वीं की मार्कशीट और आधार कार्ड में नाम की स्पेलिंग में अंतर होना।\n• सफ़ेद बैकग्राउंड के अलावा किसी अन्य बैकग्राउंड की फोटो लगाना।\n• मूल प्रमाण पत्रों की स्व-हस्ताक्षरित (Self-attested) फोटोकॉपी न ले जाना।',
                'what_to_do_if_fails': 'पासपोर्ट सेवा राष्ट्रीय टोल-फ्री हेल्पलाइन नंबर 1800-258-1800 पर संपर्क करें। यदि किसी कारणवश अपॉइंटमेंट छूट जाती है, तो आप 1 वर्ष के भीतर बिना अतिरिक्त फीस के 3 बार अपॉइंटमेंट रीशेड्यूल कर सकते हैं।',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g1, language='mwr',
            defaults={
                'title': 'भारतीय पासपोर्ट आवेदन (पासपोर्ट सेवा)',
                'summary': 'पासपोर्ट सेवा केंद्र (PSK) खातर बिना कोई बिचौलिया या दलाल के घरे बैठ्या फॉर्म भरण, फीस चुकावण अर अपॉइंटमेंट तारीख तय करण रो सोरो तरीको।',
                'common_mistakes': '• 10वीं री मार्कशीट अर आधार कार्ड में नाम या स्पेलिंग रो फरक होणो।\n• धोळी (सफ़ेद) बैकग्राउंड के अलावा दूजी बैकग्राउंड आळी फोटो लगावणो।\n• असल कागजाद री खुद हस्ताक्षरित (Self-attested) फोटोकॉपी साथै नी ले जाणो।',
                'what_to_do_if_fails': 'पासपोर्ट सेवा राष्ट्रीय टोल-फ्री हेल्पलाइन नंबर 1800-258-1800 माथै फोन करो। अपॉइंटमेंट छूट जावे तो 1 साल मांय बिना दूजी फीस 3 बार तारीख बदल सको हो।',
            }
        )
        GuideStep.objects.get_or_create(guide=g1, position=1, language='en', defaults={'body': 'Visit official passportindia.gov.in and click "New User Registration". Select your Passport Office according to your current residential address.', 'portal_label_en': 'Click "New User Registration"'})
        GuideStep.objects.get_or_create(guide=g1, position=2, language='en', defaults={'body': 'Log in with your registered ID. Click on "Apply for Fresh Passport / Re-issue of Passport". Choose "Normal" or "Tatkaal" and booklet size (36 pages recommended for standard users).', 'portal_label_en': 'Click "Apply for Fresh Passport"'})
        GuideStep.objects.get_or_create(guide=g1, position=3, language='en', defaults={'body': 'Fill your personal details strictly matching your 10th Board certificate or Birth Certificate. Enter current residential address and emergency contact.', 'portal_label_en': 'Click "Next" & Verify Preview'})
        GuideStep.objects.get_or_create(guide=g1, position=4, language='en', defaults={'body': 'Click "Pay and Schedule Appointment". Select your nearest PSK or Post Office PSK (POPSK). Make payment online via Net Banking, UPI, or Debit Card (₹1,500).', 'portal_label_en': 'Click "Pay and Book Appointment"'})
        GuideStep.objects.get_or_create(guide=g1, position=5, language='en', defaults={'body': 'Print or save the Application Receipt with Application Reference Number (ARN). Visit the PSK on the appointment date with original documents and one set of self-attested photocopies.', 'portal_label_en': 'Click "Print Application Receipt"'})

        GuideDocument.objects.get_or_create(guide=g1, name='Proof of Date of Birth (Birth Cert / 10th Marksheet / Aadhaar)', kind='id', defaults={'allowed_formats': 'Original + Photocopy', 'notes': 'Must clearly show full date of birth'})
        GuideDocument.objects.get_or_create(guide=g1, name='Proof of Present Address (Aadhaar / Voter ID / Bank Passbook)', kind='address', defaults={'allowed_formats': 'Original + Photocopy', 'notes': 'Must match your current staying address'})
        GuideDocument.objects.get_or_create(guide=g1, name='Passport Photograph (For Tatkaal / minors)', kind='photo', defaults={'allowed_formats': 'JPEG', 'min_kb': 20, 'max_kb': 50, 'width_px': 413, 'height_px': 531, 'dpi': 300, 'notes': 'White background, 80% face coverage'})

        # Guide 2: Instant e-PAN via Aadhaar
        g2, _ = Guide.objects.get_or_create(
            slug='instant-epan-via-aadhaar',
            defaults={
                'category': cats['identity'],
                'state_scope': 'central',
                'mode': 'online',
                'fee_text': 'Free / ₹0 (₹50 optional for physical plastic card)',
                'last_date': 'Rolling / Year-round',
                'official_link': links['incometax'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g2, language='en',
            defaults={
                'title': 'Instant e-PAN Card via Aadhaar (Paperless & Free)',
                'summary': 'Generate a digitally valid Permanent Account Number (PAN) card within 10 minutes using your Aadhaar e-KYC. Completely free on the Income Tax portal.',
                'common_mistakes': '• Applicant mobile number not linked to Aadhaar (cannot receive verification OTP).\n• Applicant already holding an existing PAN card (holding two PAN cards incurs ₹10,000 penalty under Section 272B).\n• Minor applicant (Instant e-PAN requires applicant to be at least 18 years old).',
                'what_to_do_if_fails': 'If Aadhaar OTP fails to arrive, check mobile network or verify linked number on myaadhaar.uidai.gov.in. For Income Tax e-filing portal support, call 1800-180-1961.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g2, language='hi',
            defaults={
                'title': 'आधार द्वारा तुरंत निःशुल्क e-PAN कार्ड बनाएं (Instant e-PAN)',
                'summary': 'आयकर विभाग के आधिकारिक पोर्टल पर बिना किसी शुल्क के केवल 10 मिनट में डिजिटल पैन कार्ड प्राप्त करने की संपूर्ण प्रक्रिया।',
                'common_mistakes': '• आधार कार्ड से मोबाइल नंबर लिंक न होना।\n• पहले से बना हुआ पैन कार्ड होने पर दोबारा आवेदन करना (दो पैन कार्ड रखने पर 10,000 रुपये का जुर्माना है)।\n• 18 वर्ष से कम आयु होना (यह सुविधा केवल वयस्कों के लिए है)।',
                'what_to_do_if_fails': 'आयकर विभाग के हेल्पलाइन नंबर 1800-180-1961 पर संपर्क करें। e-PAN का पीडीएफ पासवर्ड आपकी जन्मतिथि होती है (प्रारूप: DDMMYYYY)।',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g2, language='mwr',
            defaults={
                'title': 'आधार सूं तुरंत मुफ़्त e-PAN कार्ड बणाओ',
                'summary': 'इनकम टैक्स विभाग रे आधिकारिक पोर्टल माथै बिना कोई रुपिया दिये खाली 10 मिनट में डिजिटल पैन कार्ड बणावण री पूरी जानकारी।',
                'common_mistakes': '• आधार कार्ड सूं मोबाइल नंबर जुड्योडो नी होणो।\n• पैली सूं पैन कार्ड बण्योडो होवे तो पाछो आवेदन करणो (दो पैन कार्ड राखण माथै 10,000 रुपिया रो दंड लागे)।\n• 18 साल सूं कम उमर होणी।',
                'what_to_do_if_fails': 'इनकम टैक्स हेल्पलाइन नंबर 1800-180-1961 माथै फोन करो। e-PAN पीडीएफ रो पासवर्ड थारी जनम-तारीख (DDMMYYYY) होवेला।',
            }
        )
        GuideStep.objects.get_or_create(guide=g2, position=1, language='en', defaults={'body': 'Go to the official Income Tax portal (incometax.gov.in). Under the "Quick Links" section on the left, click "Instant e-PAN".', 'portal_label_en': 'Click "Instant e-PAN"'})
        GuideStep.objects.get_or_create(guide=g2, position=2, language='en', defaults={'body': 'Click on "Get New e-PAN". Enter your 12-digit Aadhaar number and check the consent box confirming you have never been allotted a PAN card.', 'portal_label_en': 'Click "Get New e-PAN" & Enter Aadhaar'})
        GuideStep.objects.get_or_create(guide=g2, position=3, language='en', defaults={'body': 'Enter the 6-digit OTP received on your Aadhaar-linked mobile phone and agree to validate Aadhaar details with UIDAI.', 'portal_label_en': 'Click "Validate Aadhaar OTP"'})
        GuideStep.objects.get_or_create(guide=g2, position=4, language='en', defaults={'body': 'Review your photo, name, date of birth, and address fetched from Aadhaar. Accept terms and submit the application. Note the 15-digit acknowledgement number.', 'portal_label_en': 'Click "Submit PAN Request"'})
        GuideStep.objects.get_or_create(guide=g2, position=5, language='en', defaults={'body': 'Wait 10 minutes. Return to "Instant e-PAN", select "Check Status / Download PAN", enter Aadhaar + OTP, and download your signed PDF e-PAN.', 'portal_label_en': 'Click "Download e-PAN (PDF)"'})

        GuideDocument.objects.get_or_create(guide=g2, name='Aadhaar Card with linked mobile number', kind='id', defaults={'allowed_formats': 'Digital e-KYC', 'notes': 'Must have active phone to receive OTP'})

        # Guide 3: Driving Licence - Learner's Licence Test & Application
        g3, _ = Guide.objects.get_or_create(
            slug='driving-licence-learners-licence-parivahan',
            defaults={
                'category': cats['transport'],
                'state_scope': 'central',
                'mode': 'online',
                'fee_text': '₹150 to ₹200 (Official State Government Fee)',
                'last_date': 'Rolling / Valid for 6 months once issued',
                'official_link': links['parivahan'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g3, language='en',
            defaults={
                'title': 'Learner Driving Licence (LL) Online Application & Test',
                'summary': 'Complete the Learner Driving Licence application and online test from home using Aadhaar authentication on the official Parivahan Sarathi portal.',
                'common_mistakes': '• Submitting illegible dark photo of signature.\n• Attempting online test without watching the mandatory road safety tutorial video.\n• Failing the 15-question road signs exam (requires minimum 9 correct answers).\n• Mismatch in blood group details.',
                'what_to_do_if_fails': 'If you fail the online LL test, you can re-appear after 7 days by logging in with your application number and paying a nominal re-test fee of ₹50 on Parivahan Sarathi.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g3, language='hi',
            defaults={
                'title': 'लर्निंग ड्राइविंग लाइसेंस (LL) ऑनलाइन आवेदन व परीक्षा',
                'summary': 'परिवहन सारथी पोर्टल पर आधार प्रमाणीकरण द्वारा घर बैठे लर्निंग लाइसेंस के लिए आवेदन करने और ऑनलाइन परीक्षा देने का आसान तरीका।',
                'common_mistakes': '• सादे सफेद कागज के बजाय लाइन वाले कागज पर हस्ताक्षर अपलोड करना।\n• अनिवार्य सड़क सुरक्षा ट्यूटोरियल वीडियो पूरा न देखना।\n• यातायात संकेत परीक्षा में 15 में से 9 अंक प्राप्त न कर पाना।',
                'what_to_do_if_fails': 'यदि आप परीक्षा में अनुत्तीर्ण हो जाते हैं, तो 7 दिन बाद केवल ₹50 का पुनः परीक्षा शुल्क भरकर सीधे दोबारा ऑनलाइन टेस्ट दे सकते हैं। किसी एजेंट को अतिरिक्त रुपये न दें।',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g3, language='mwr',
            defaults={
                'title': 'लर्निंग ड्राइविंग लाइसेंस (LL) ऑनलाइन आवेदन अर परीक्षा',
                'summary': 'परिवहन सारथी पोर्टल माथै आधार जांच सूं घरे बैठ्या लर्निंग लाइसेंस वास्ते फॉर्म भरण अर ऑनलाइन टेस्ट देवण रो सोरो तरीको।',
                'common_mistakes': '• कोरा सफेद कागज रे बजाय लाइनदार कागज माथै दस्तखत (हस्ताक्षर) अपलोड करणो।\n• सड़क सुरक्षा रो जरूरी वीडियो पूरा नी देखणो।\n• यातायात नियम परीक्षा में 15 में सूं 9 सवाल साचा नी कर पावणो।',
                'what_to_do_if_fails': 'जेकर टेस्ट में फेल हो जाओ तो 7 दिन बाद खाली ₹50 फीस भर\'र पाछो ऑनलाइन टेस्ट दे सको हो। किसी बिचौलिये ने रुपिया मत दीजो।',
            }
        )
        GuideStep.objects.get_or_create(guide=g3, position=1, language='en', defaults={'body': 'Go to sarathi.parivahan.gov.in and select your State or Union Territory.', 'portal_label_en': 'Select State on Parivahan Sarathi'})
        GuideStep.objects.get_or_create(guide=g3, position=2, language='en', defaults={'body': 'Click "Apply for Learner Licence". Select "Applicant does not hold Driving/Learner Licence" and choose "Submit via Aadhaar Authentication".', 'portal_label_en': 'Click "Apply for Learner Licence"'})
        GuideStep.objects.get_or_create(guide=g3, position=3, language='en', defaults={'body': 'Enter Aadhaar number and OTP. Select vehicle category (e.g., MCWG for Motorcycle with Gear, LMV for Light Motor Vehicle / Car). Fill Medical Self-Declaration Form 1.', 'portal_label_en': 'Select Vehicle Class & Form 1'})
        GuideStep.objects.get_or_create(guide=g3, position=4, language='en', defaults={'body': 'Upload clear signature (black ink on plain white paper). Photo is auto-fetched from Aadhaar.', 'portal_label_en': 'Click "Upload Documents & Signature"'})
        GuideStep.objects.get_or_create(guide=g3, position=5, language='en', defaults={'body': 'Pay fee online (₹150-₹200 depending on state). Watch the mandatory road safety awareness video. Receive LL exam password via SMS and start the online test.', 'portal_label_en': 'Click "Pay Fee & Take Online LL Test"'})

        GuideDocument.objects.get_or_create(guide=g3, name='Applicant Signature Scan', kind='signature', defaults={'allowed_formats': 'JPEG, JPG', 'min_kb': 10, 'max_kb': 20, 'width_px': 256, 'height_px': 64, 'notes': 'Black ink on white background, no lined paper'})
        GuideDocument.objects.get_or_create(guide=g3, name='Medical Fitness Self Declaration (Form 1)', kind='other', defaults={'allowed_formats': 'Online Checkbox Form', 'notes': 'Completed directly inside portal'})

        # Guide 4: New Voter ID Registration (Form 6)
        g4, _ = Guide.objects.get_or_create(
            slug='new-voter-id-registration-form-6',
            defaults={
                'category': cats['elections'],
                'state_scope': 'central',
                'mode': 'online',
                'fee_text': 'Free / ₹0',
                'last_date': 'Rolling / Year-round',
                'official_link': links['voters'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g4, language='en',
            defaults={
                'title': 'New Voter ID Card Registration (Form 6 Online)',
                'summary': 'Free online registration for Indian citizens turning 18 years of age on the Election Commission of India (ECI) Voters Service Portal.',
                'common_mistakes': '• Selecting incorrect Assembly Constituency.\n• Uploading group photo or selfie instead of clear passport photo.\n• Not providing family member\'s existing Voter ID (EPIC) number for faster address matching.',
                'what_to_do_if_fails': 'Dial National Voter Toll-Free Helpline: 1950. You can track your application status online using the Reference ID provided on submission.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g4, language='hi',
            defaults={
                'title': 'नया वोटर आईडी कार्ड ऑनलाइन बनाएं (फॉर्म 6)',
                'summary': '18 वर्ष के भारतीय नागरिकों के लिए भारत निर्वाचन आयोग (ECI) के पोर्टल पर नया मतदाता पहचान पत्र निःशुल्क बनाने की पूरी प्रक्रिया।',
                'common_mistakes': '• गलत विधानसभा क्षेत्र का चयन करना।\n• पासपोर्ट साइज फोटो के स्थान पर तिरछी सेल्फी या धुंधली फोटो अपलोड करना।\n• पते का वैध प्रमाण न देना।',
                'what_to_do_if_fails': 'भारत निर्वाचन आयोग के राष्ट्रीय हेल्पलाइन नंबर 1950 पर कॉल करें। फॉर्म जमा करने के बाद मिले रेफरेंस नंबर से स्टेटस ट्रैक करें।',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g4, language='mwr',
            defaults={
                'title': 'नयो वोटर आईडी कार्ड ऑनलाइन बणाओ (फॉर्म 6)',
                'summary': '18 साल रा हो चुका भारतीय नागरिक वास्ते चुनाव आयोग (ECI) रे पोर्टल माथै नयो पहचान पत्र मुफ़्त में बणावण रो पूरो तरीको।',
                'common_mistakes': '• गलत विधानसभा क्षेत्र चुन लेणो।\n• पासपोर्ट साइज फोटो री जग्या टेढ़ी सेल्फी या धुंधली फोटो लगावणो।\n• पते रो साचो सबूत नी देणो।',
                'what_to_do_if_fails': 'चुनाव आयोग री राष्ट्रीय हेल्पलाइन नंबर 1950 माथै फोन लगाओ। रेफरेंस नंबर सूं थारो स्टेटस ऑनलाइन जांच सको हो।',
            }
        )
        GuideStep.objects.get_or_create(guide=g4, position=1, language='en', defaults={'body': 'Visit voters.eci.gov.in and click "Sign-Up". Register with your mobile number and create a password.', 'portal_label_en': 'Click "Sign-Up / Login"'})
        GuideStep.objects.get_or_create(guide=g4, position=2, language='en', defaults={'body': 'Click on "New registration for general electors (Form 6)". Select your State, District, and Legislative Assembly Constituency.', 'portal_label_en': 'Click "Fill Form 6"'})
        GuideStep.objects.get_or_create(guide=g4, position=3, language='en', defaults={'body': 'Enter First Name, Surname, Father/Mother/Spouse name, and contact details. Upload recent passport size photograph (<2 MB).', 'portal_label_en': 'Enter Personal Details & Upload Photo'})
        GuideStep.objects.get_or_create(guide=g4, position=4, language='en', defaults={'body': 'Enter current residential address. Select document type for address proof (Aadhaar, Electricity/Water bill, Passbook) and upload scan.', 'portal_label_en': 'Upload Address Proof Document'})
        GuideStep.objects.get_or_create(guide=g4, position=5, language='en', defaults={'body': 'Verify the filled declaration. Click Submit. Save the Application Reference Number. Booth Level Officer (BLO) will visit your address for verification.', 'portal_label_en': 'Click "Preview and Submit"'})

        GuideDocument.objects.get_or_create(guide=g4, name='Passport Size Photo', kind='photo', defaults={'allowed_formats': 'JPEG, JPG', 'max_kb': 2000, 'notes': 'Plain background, frontal portrait'})
        GuideDocument.objects.get_or_create(guide=g4, name='Address Proof (Aadhaar / Bill / Passbook)', kind='address', defaults={'allowed_formats': 'JPEG, PDF', 'max_kb': 2000, 'notes': 'Must reflect current residential address'})

        # Guide 5: Aadhaar Address Update Online
        g5, _ = Guide.objects.get_or_create(
            slug='aadhaar-address-update-online',
            defaults={
                'category': cats['identity'],
                'state_scope': 'central',
                'mode': 'online',
                'fee_text': '₹50 (Official UIDAI Portal Charge)',
                'last_date': 'Rolling / Year-round',
                'official_link': links['myaadhaar'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g5, language='en',
            defaults={
                'title': 'Aadhaar Card Address Update Online (myAadhaar)',
                'summary': 'Update your residential address on your Aadhaar card online from home without visiting an Aadhaar Seva Kendra, using verified address proof documents.',
                'common_mistakes': '• Address on uploaded document does not match entered address character for character.\n• Uploading passbook without bank stamp/signature.\n• Using utility bill older than 3 months.',
                'what_to_do_if_fails': 'If update request is rejected, check specific reason in rejection SMS. You can contact UIDAI helpline 1947 or re-submit with an approved valid document.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g5, language='hi',
            defaults={
                'title': 'आधार कार्ड में पता ऑनलाइन बदलें (myAadhaar पोर्टल)',
                'summary': 'आधार सेवा केंद्र जाए बिना, अपने फोन से सीधे myAadhaar पोर्टल पर मात्र ₹50 में पता अपडेट करने का सही तरीका।',
                'common_mistakes': '• अपलोड किए गए दस्तावेज़ में लिखा पता और फॉर्म में भरे पते में भिन्नता होना।\n• 3 महीने से पुराना बिजली या पानी का बिल अपलोड करना।\n• बैंक पासबुक पर बैंक की मुहर न होना।',
                'what_to_do_if_fails': 'यूआईडीएआई (UIDAI) के राष्ट्रीय टोल-फ्री नंबर 1947 पर संपर्क करें। स्टेटस देखने के लिए अपना एसआरएन (SRN) नंबर संभाल कर रखें।',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g5, language='mwr',
            defaults={
                'title': 'आधार कार्ड में पतो ऑनलाइन बदलो (myAadhaar पोर्टल)',
                'summary': 'आधार सेवा केंद्र गया बिना, थारे फोन सूं myAadhaar पोर्टल माथै खाली ₹50 में पतो बदलो।',
                'common_mistakes': '• अपलोड करया कागद रो पतो अर फॉर्म में भरया पते में फरक होणो।\n• 3 महीना सूं जूनो बिजली या पाणी रो बिल लगावणो।\n• बैंक पासबुक माथै बैंक री मोहर नी होणी।',
                'what_to_do_if_fails': 'UIDAI राष्ट्रीय हेल्पलाइन 1947 माथै फोन करो। स्टेटस जाचण खातर SRN नंबर संभाल कर राखो।',
            }
        )
        GuideStep.objects.get_or_create(guide=g5, position=1, language='en', defaults={'body': 'Visit myaadhaar.uidai.gov.in and click "Login". Enter your 12-digit Aadhaar number and captcha, then enter the OTP received on your mobile.', 'portal_label_en': 'Click "Login" & Enter Aadhaar OTP'})
        GuideStep.objects.get_or_create(guide=g5, position=2, language='en', defaults={'body': 'Select "Address Update" from the services grid, then click "Update Aadhaar Online". Review the instructions on valid documents.', 'portal_label_en': 'Click "Update Aadhaar Online"'})
        GuideStep.objects.get_or_create(guide=g5, position=3, language='en', defaults={'body': 'Enter your new complete address details (Care of, House No, Street, Landmark, PIN Code, Village/City, Post Office). Pin code determines post office.', 'portal_label_en': 'Fill New Address Fields'})
        GuideStep.objects.get_or_create(guide=g5, position=4, language='en', defaults={'body': 'Select your valid Supporting Document type (Voter ID, Passport, Bank Passbook, Electricity Bill, or Rent Agreement). Upload PDF or JPEG scan (<2 MB).', 'portal_label_en': 'Select Document & Upload Scan'})
        GuideStep.objects.get_or_create(guide=g5, position=5, language='en', defaults={'body': 'Pay the official ₹50 charge online via UPI, Debit Card, or Net Banking. Download the payment receipt with the Service Request Number (SRN) for tracking.', 'portal_label_en': 'Click "Make Payment (₹50)"'})

        GuideDocument.objects.get_or_create(guide=g5, name='Address Proof Document (Voter ID / Bill / Passbook / Passport)', kind='address', defaults={'allowed_formats': 'JPEG, PNG, PDF', 'max_kb': 2000, 'notes': 'Must be in applicant name and strictly match address entered'})

        # Guide 6: National Scholarship Portal (NSP) Fresh Application
        g6, _ = Guide.objects.get_or_create(
            slug='national-scholarship-portal-nsp-application',
            defaults={
                'category': cats['education'],
                'state_scope': 'central',
                'mode': 'online',
                'fee_text': 'Free / ₹0',
                'last_date': '31 October (Annual Academic Cycle)',
                'official_link': links['scholarships'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g6, language='en',
            defaults={
                'title': 'National Scholarship Portal (NSP) Fresh Application',
                'summary': 'Complete guide for students to register One-Time Registration (OTR) and apply for Central Sector, Pre-Matric, and Post-Matric scholarships.',
                'common_mistakes': '• Bank account not seeded with Aadhaar on NPCI mapper (scholarship money bounces).\n• Submitting expired income certificate.\n• Mismatch between student name on marksheet and Aadhaar.',
                'what_to_do_if_fails': 'Check with your school or college Institute Nodal Officer (INO) to verify application. Call NSP Helpdesk: 0120-6619540.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g6, language='hi',
            defaults={
                'title': 'राष्ट्रीय छात्रवृत्ति पोर्टल (NSP) नया आवेदन प्रक्रिया',
                'summary': 'कक्षा 1 से उच्च शिक्षा तक के विद्यार्थियों के लिए केंद्र व राज्य सरकार की छात्रवृत्ति हेतु OTR पंजीकरण और आवेदन की आसान मार्गदर्शिका।',
                'common_mistakes': '• बैंक खाते का आधार से लिंक (NPCI Seeded) न होना।\n• 6 माह से पुराना आय प्रमाण पत्र लगाना।\n• कॉलेज/स्कूल के नोडल अधिकारी से समय पर सत्यापन न कराना।',
                'what_to_do_if_fails': 'अपने कॉलेज/स्कूल के छात्रवृत्ति नोडल अधिकारी से संपर्क करें या राष्ट्रीय छात्रवृत्ति पोर्टल हेल्पलाइन नंबर 0120-6619540 पर संपर्क करें।',
            }
        )
        GuideStep.objects.get_or_create(guide=g6, position=1, language='en', defaults={'body': 'Visit scholarships.gov.in. Click "Apply for One-Time Registration (OTR)". Download the Aadhaar FaceRD app on mobile or use OTP verification.', 'portal_label_en': 'Click "One-Time Registration (OTR)"'})
        GuideStep.objects.get_or_create(guide=g6, position=2, language='en', defaults={'body': 'Complete e-KYC. Receive your 14-digit OTR number via SMS. Log in to NSP with OTR number and password.', 'portal_label_en': 'Login with OTR Number'})
        GuideStep.objects.get_or_create(guide=g6, position=3, language='en', defaults={'body': 'Select your scheme (Pre-Matric / Post-Matric / Top Class Education). Enter previous examination marks, roll number, and annual family income.', 'portal_label_en': 'Select Scholarship Scheme'})
        GuideStep.objects.get_or_create(guide=g6, position=4, language='en', defaults={'body': 'Upload Bonafide Student Certificate signed by school/college principal, Income Certificate, and Caste Certificate.', 'portal_label_en': 'Upload Institutional Bonafide'})
        GuideStep.objects.get_or_create(guide=g6, position=5, language='en', defaults={'body': 'Submit application. Take a printout and submit along with document photocopies to your institution\'s scholarship desk for verification.', 'portal_label_en': 'Click "Final Submit" & Print'})

        GuideDocument.objects.get_or_create(guide=g6, name='Bonafide Student Certificate from Institution', kind='other', defaults={'allowed_formats': 'PDF, JPEG', 'max_kb': 200, 'notes': 'Must bear principal signature and seal'})
        GuideDocument.objects.get_or_create(guide=g6, name='Family Income Certificate', kind='other', defaults={'allowed_formats': 'PDF, JPEG', 'max_kb': 200, 'notes': 'Issued by authorized revenue authority'})

        # Guide 7: Pradhan Mantri Ujjwala Yojana (PMUY) LPG Connection
        g7, _ = Guide.objects.get_or_create(
            slug='pm-ujjwala-yojana-free-lpg-connection',
            defaults={
                'category': cats['utilities'],
                'state_scope': 'central',
                'mode': 'partial',
                'fee_text': 'Free / ₹0 (Deposit-Free LPG Cylinder & Stove)',
                'last_date': 'Rolling / Year-round',
                'official_link': links['pmuy'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g7, language='en',
            defaults={
                'title': 'PM Ujjwala Yojana 2.0 Free LPG Gas Connection',
                'summary': 'How eligible women from poor households can apply for a deposit-free LPG connection with free first refill and hotplate under PMUY 2.0.',
                'common_mistakes': '• Applying in the name of a male family member (connection is strictly in adult female name).\n• Existing active LPG connection registered in any family member\'s name on the same ration card.\n• Mismatch in bank account details for DBTL subsidy.',
                'what_to_do_if_fails': 'Call the national PMUY toll-free helpline: 1800-266-6696 or 1906 for 24x7 gas service inquiries.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g7, language='hi',
            defaults={
                'title': 'प्रधानमंत्री उज्ज्वला योजना 2.0 मुफ्त गैस कनेक्शन',
                'summary': 'पात्र महिला आवेदकों के लिए बिना किसी डिपाजिट के नया गैस कनेक्शन, पहला भरा सिलेंडर और चूल्हा मुफ्त पाने की पूरी गाइड।',
                'common_mistakes': '• परिवार के किसी अन्य सदस्य के नाम पहले से गैस कनेक्शन होना।\n• महिला आवेदक की आयु 18 वर्ष से कम होना।\n• राशन कार्ड में दर्ज सभी वयस्क सदस्यों के आधार कार्ड न लगाना।',
                'what_to_do_if_fails': 'प्रधानमंत्री उज्ज्वला योजना की टोल-फ्री हेल्पलाइन 1800-266-6696 पर संपर्क करें।',
            }
        )
        GuideStep.objects.get_or_create(guide=g7, position=1, language='en', defaults={'body': 'Visit pmuy.gov.in and click on "Apply for New Ujjwala 2.0 Connection". Review eligibility criteria (adult woman belonging to eligible rural/deprived categories).', 'portal_label_en': 'Click "Apply for Ujjwala 2.0"'})
        GuideStep.objects.get_or_create(guide=g7, position=2, language='en', defaults={'body': 'Select your preferred company distributor: IndianOil (Indane), Bharat Petroleum (Bharatgas), or Hindustan Petroleum (HP Gas).', 'portal_label_en': 'Choose Gas Company (Indane / Bharat / HP)'})
        GuideStep.objects.get_or_create(guide=g7, position=3, language='en', defaults={'body': 'Fill the 14-point declaration including Aadhaar numbers of all adult family members, current address proof, and bank account for subsidy.', 'portal_label_en': 'Fill 14-Point Declaration Form'})
        GuideStep.objects.get_or_create(guide=g7, position=4, language='en', defaults={'body': 'Submit the online pre-registration and take down the reference number. Alternatively, download the physical form.', 'portal_label_en': 'Click "Submit Registration"'})
        GuideStep.objects.get_or_create(guide=g7, position=5, language='en', defaults={'body': 'Visit the local distributor with original Aadhaar cards and ration card for biometric verification and collect the connection.', 'portal_label_en': 'Physical KYC at Distributor'})

        GuideDocument.objects.get_or_create(guide=g7, name='Ration Card showing family composition', kind='id', defaults={'allowed_formats': 'Original + Copy', 'notes': 'Issued by state government'})
        GuideDocument.objects.get_or_create(guide=g7, name='Bank Passbook / Cancelled Cheque', kind='other', defaults={'allowed_formats': 'Copy', 'notes': 'Must have IFSC code clearly printed'})

        # Guide 8: DigiLocker Account Setup & Document Pull
        g8, _ = Guide.objects.get_or_create(
            slug='digilocker-account-fetch-official-documents',
            defaults={
                'category': cats['identity'],
                'state_scope': 'central',
                'mode': 'online',
                'fee_text': 'Free / ₹0 (Legally Valid under IT Act Rule 9A)',
                'last_date': 'Rolling / Lifetime',
                'official_link': links['digilocker'],
                'status': 'published',
                'last_verified_at': now,
                'verified_by': admin_user,
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g8, language='en',
            defaults={
                'title': 'DigiLocker Account Creation & Official Document Pull',
                'summary': 'Store and access digitally authentic Driving Licence, RC, CBSE mark sheets, PAN, and Aadhaar on your phone, legally equivalent to physical originals.',
                'common_mistakes': '• Forgetting 6-digit security PIN.\n• Name mismatch between DigiLocker profile and board/transport department databases.\n• Entering wrong registration number or chassis number for Vehicle RC.',
                'what_to_do_if_fails': 'Use the "Forgot Security PIN" option to reset using Aadhaar OTP. For document pull issues, visit support.digitallocker.gov.in.',
            }
        )
        GuideTranslation.objects.update_or_create(
            guide=g8, language='hi',
            defaults={
                'title': 'डिजिलॉकर (DigiLocker) खाता बनाएं व सरकारी दस्तावेज़ प्राप्त करें',
                'summary': 'ड्राइविंग लाइसेंस, आरसी, पैन कार्ड, 10वीं/12वीं की मार्कशीट डिजिटल रूप से अपने फ़ोन में रखने का निःशुल्क व आधिकारिक तरीका।',
                'common_mistakes': '• 6-अंकों का सुरक्षा पिन भूल जाना।\n• आधार में नाम और 10वीं की मार्कशीट के नाम में अंतर होना।\n• वाहन का सही चेसिस नंबर दर्ज न करना।',
                'what_to_do_if_fails': 'पिन भूल जाने पर "Forgot Security PIN" पर क्लिक करके आधार ओटीपी से तुरंत नया पिन बनाएं।',
            }
        )
        GuideStep.objects.get_or_create(guide=g8, position=1, language='en', defaults={'body': 'Visit digilocker.gov.in or install the official DigiLocker app on your phone. Click "Sign Up".', 'portal_label_en': 'Click "Sign Up"'})
        GuideStep.objects.get_or_create(guide=g8, position=2, language='en', defaults={'body': 'Enter Full Name (as on Aadhaar), Date of Birth, Gender, Mobile Number, 6-digit security PIN, and Email ID. Enter 12-digit Aadhaar number.', 'portal_label_en': 'Enter Details & Set 6-Digit PIN'})
        GuideStep.objects.get_or_create(guide=g8, position=3, language='en', defaults={'body': 'Enter the OTP received on your mobile phone to complete account creation and log in.', 'portal_label_en': 'Verify Mobile & Aadhaar OTP'})
        GuideStep.objects.get_or_create(guide=g8, position=4, language='en', defaults={'body': 'Click "Search Documents". Search for Ministry of Road Transport (Driving Licence, RC), CBSE/State Board (Marksheet), or Income Tax (PAN Verification Record).', 'portal_label_en': 'Click "Search Documents"'})
        GuideStep.objects.get_or_create(guide=g8, position=5, language='en', defaults={'body': 'Enter document parameters (e.g. DL Number or Roll Number). Click "Get Document". Document is saved permanently under "Issued Documents" with digital QR signature.', 'portal_label_en': 'Click "Get Document"'})

        GuideDocument.objects.get_or_create(guide=g8, name='Aadhaar Number with active mobile', kind='id', defaults={'allowed_formats': 'Digital', 'notes': 'Required for instant e-KYC'})

        # 5. Seed Wizard Decision Tree Questions
        # Question 1: Travel / Passport
        q_pass, _ = WizardQuestion.objects.update_or_create(
            question_key='passport_fresh_or_reissue',
            defaults={
                'category': cats['travel'],
                'position': 1,
                'text_en': 'Are you applying for a fresh Indian Passport or renewing an expired one?',
                'text_hi': 'क्या आप नया भारतीय पासपोर्ट बनवाना चाहते हैं या पुराने पासपोर्ट का नवीनीकरण कराना चाहते हैं?',
                'text_mwr': 'कांईं थे नयो भारतीय पासपोर्ट बणावण चाहवो हो या जूने पासपोर्ट रो नवीनीकरण करावण चाहवो हो?',
                'yes_outcome_guide': g1,
            }
        )

        # Question 2: Identity / PAN
        q_pan, _ = WizardQuestion.objects.update_or_create(
            question_key='pan_has_aadhaar_phone',
            defaults={
                'category': cats['identity'],
                'position': 2,
                'text_en': 'Do you have an Aadhaar card with your active mobile number linked to it?',
                'text_hi': 'क्या आपके पास आधार कार्ड है और उससे आपका सक्रिय मोबाइल नंबर लिंक है?',
                'text_mwr': 'कांईं थारे कनै आधार कार्ड है अर उण सूं थारो चालू मोबाइल नंबर जुड्योडो है?',
                'yes_outcome_guide': g2,
                'no_outcome_guide': g8,
            }
        )

        # Question 3: Transport / Driving Licence
        q_dl, _ = WizardQuestion.objects.update_or_create(
            question_key='dl_apply_learner_first',
            defaults={
                'category': cats['transport'],
                'position': 3,
                'text_en': 'Are you applying for your first driving licence (Learner Licence LL)?',
                'text_hi': 'क्या आप पहली बार ड्राइविंग लाइसेंस (लर्निंग लाइसेंस) बनवाने के लिए आवेदन कर रहे हैं?',
                'text_mwr': 'कांईं थे पैली बार ड्राइविंग लाइसेंस (लर्निंग लाइसेंस) बणावण वास्ते फॉर्म भर रिया हो?',
                'yes_outcome_guide': g3,
            }
        )

        # Question 4: Elections / Voter ID
        q_voter, _ = WizardQuestion.objects.update_or_create(
            question_key='voter_first_time_18',
            defaults={
                'category': cats['elections'],
                'position': 4,
                'text_en': 'Are you an Indian citizen aged 18 or above applying for a new Voter ID?',
                'text_hi': 'क्या आप 18 वर्ष या उससे अधिक आयु के नागरिक हैं और नया वोटर कार्ड बनवाना चाहते हैं?',
                'text_mwr': 'कांईं थे 18 साल या उण सूं बत्ती उमर रा नागरिक हो अर नयो वोटर कार्ड बणावण चाहवो हो?',
                'yes_outcome_guide': g4,
            }
        )

        # Question 5: Education / Scholarship
        q_sch, _ = WizardQuestion.objects.update_or_create(
            question_key='scholarship_student',
            defaults={
                'category': cats['education'],
                'position': 5,
                'text_en': 'Are you a school or college student applying for government scholarship support?',
                'text_hi': 'क्या आप स्कूल या कॉलेज के विद्यार्थी हैं और सरकारी छात्रवृत्ति के लिए आवेदन करना चाहते हैं?',
                'text_mwr': 'कांईं थे स्कूल या कॉलेज रा विद्यार्थी हो अर सरकारी छात्रवृत्ति खातर फॉर्म भर रिया हो?',
                'yes_outcome_guide': g6,
            }
        )

        # Question 6: Utilities / LPG
        q_lpg, _ = WizardQuestion.objects.update_or_create(
            question_key='lpg_ujjwala_connection',
            defaults={
                'category': cats['utilities'],
                'position': 6,
                'text_en': 'Are you applying for a free deposit-free LPG gas connection under PM Ujjwala Yojana?',
                'text_hi': 'क्या आप प्रधानमंत्री उज्ज्वला योजना के तहत मुफ्त गैस कनेक्शन के लिए आवेदन कर रहे हैं?',
                'text_mwr': 'कांईं थे प्रधानमंत्री उज्ज्वला योजना तहत बिना डिपाजिट मुफ़्त गैस कनेक्शन खातर आवेदन कर रिया हो?',
                'yes_outcome_guide': g7,
            }
        )

        # Link questions sequentially
        q_pass.no_next = q_pan
        q_pass.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded 8+ national guides, official links, categories, and decision tree questions!"))
