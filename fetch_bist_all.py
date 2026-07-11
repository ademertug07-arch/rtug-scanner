#!/usr/bin/env python3
"""
BIST Tum Hisse Senetlerini Yahoo Finance'den Cek
=================================================
Yahoo Finance'de .IS uzantisi ile islem goren tum BIST hisselerini dener.
"""

import yfinance as yf
import time
import json
from typing import List

# Bilinen BIST hisseleri (alfabetik, surekli guncellenir)
# Kaynak: Mynet Finans, CNN Turk, TradingView
BIST_ALL = [
    "A1CAP", "A1YEN", "AAGYO", "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES",
    "AFYON", "AGESA", "AGHOL", "AGROT", "AGYO", "AHGAZ", "AHSGY", "AKBNK",
    "AKCNS", "AKENR", "AKFGY", "AKFIS", "AKFYE", "AKGRT", "AKHAN", "AKMGY",
    "AKSA", "AKSEN", "AKSGY", "AKSUE", "AKYHO", "ALARK", "ALBRK", "ALCAR",
    "ALCTL", "ALFAS", "ALGYO", "ALKA", "ALKIM", "ALKLC", "ALTNY", "ALVES",
    "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK", "ARDYZ", "ARENA",
    "ARFYE", "ARMGD", "ARSAN", "ARTMS", "ARZUM", "ASELS", "ASGYO", "ASTOR",
    "ASUZU", "ATAGY", "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO",
    "AVHOL", "AVOD", "AVPGY", "AYCES", "AYDEM", "AYEN", "AYES", "AYGAZ",
    "AZTEK", "BAGFS", "BAHKM", "BAKAB", "BALAT", "BALSU", "BANVT", "BARMA",
    "BASCM", "BASGZ", "BAYRK", "BEGYO", "BERA", "BESLR", "BETAE", "BEYAZ",
    "BFREN", "BIENY", "BIGCH", "BIGEN", "BIMAS", "BIOEN", "BINBN", "BINHO",
    "BJKAS", "BMSCH", "BMSTL", "BORSK", "BOSS1", "BOTAS", "BOYNR", "BRISA",
    "BRKSN", "BRSAN", "BRVGY", "BUCIM", "BURCE", "BURVA", "BVDVA", "BYDNR",
    "CANTE", "CARFA", "CASA", "CATES", "CCOLA", "CELHA", "CEMTS", "CEOEM",
    "CETIM", "CGCAM", "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO",
    "CRDFA", "CRFSA", "CVKMD", "CYBLN", "DAGHL", "DAGI", "DAPGM", "DARDL",
    "DBSAN", "DENGE", "DERIM", "DERHL", "DESA", "DESPC", "DEVA", "DFACT",
    "DGGYO", "DIRIT", "DITAS", "DMSAS", "DOBUR", "DOCO", "DOFER", "DOGUB",
    "DOHOL", "DOKTA", "DURDO", "DYOBY", "DZGYO", "ECILC", "ECZYT", "EDATA",
    "EDIP", "EFORC", "EGEEN", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKGYO",
    "EKIMM", "EKKLY", "EKSUN", "ELCBK", "ELITE", "EMKEL", "EMMRK", "EMNIS",
    "ENERY", "ENJSA", "ENKAI", "ENKU", "EPLAS", "ERBOS", "ERCB", "EREGL",
    "ERSU", "ERTGL", "ESCOM", "ESEN", "ESGAY", "ETILR", "ETYAT", "EUHOL",
    "EUKYO", "EUYO", "EVKUR", "EVTEN", "EYGYO", "EZC2B", "EZCT", "FADE",
    "FENER", "FHLGY", "FLAP", "FMIZP", "FONET", "FORTE", "FROTO", "FRVGO",
    "FZLGY", "GALAT", "GARAN", "GARFA", "GARFO", "GEDIK", "GEDZA", "GENIL",
    "GENTS", "GEREL", "GIPTA", "GLBMD", "GLRYH", "GMTAS", "GOLTS", "GOODY",
    "GOZDE", "GRNYO", "GRSA", "GRTRK", "GRUBO", "GSDHO", "GSRAY", "GUBRF",
    "GUKCR", "GULBM", "GUNDF", "GUSGR", "GWIND", "HALKB", "HATSN", "HDFGS",
    "HEDEF", "HEDEH", "HEKTS", "HKTM", "HLGYO", "HOROZ", "HRKET", "HRZTF",
    "HUBVC", "HURGZ", "HUNER", "HYDRO", "HYGYN", "IEGCY", "IEYHO", "IGCGS",
    "IGSAS", "IHAAS", "IKTAS", "IMASM", "INDES", "INFRA", "INGYO", "INTEK",
    "INTFA", "INVEO", "INVES", "IPLKY", "ISATR", "ISBIR", "ISBTR", "ISCTR",
    "ISDMR", "ISFIN", "ISGSY", "ISGYO", "ISIST", "ISKPL", "ISKUR", "ISMEN",
    "ISSEN", "ISYAT", "IZENR", "IZFAS", "IZINV", "IZMDC", "JANTS", "KAPLM",
    "KAREL", "KARSN", "KARTN", "KATMR", "KAYSE", "KBORU", "KCAER", "KCHOL",
    "KENT", "KERVN", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLKIM", "KLMSN",
    "KLNMA", "KLRHO", "KLSER", "KLSYN", "KLYPV", "KMPUR", "KNFRT", "KOCMT",
    "KONKA", "KONTR", "KONYA", "KOPOL", "KORDS", "KOTON", "KRDMA", "KRDMB",
    "KRDMD", "KRGYO", "KRONT", "KRPLS", "KRSTL", "KRTEK", "KRVGD", "KSTUR",
    "KTLEV", "KTSKR", "KUTPO", "KUVVA", "KUYAS", "KZBGY", "LIDER", "LIDFA",
    "LILAK", "LINK", "LKMNH", "LMKDC", "LOGO", "LRSHO", "LUKSK", "LXGYO",
    "LYDHO", "LYDYE", "MAALT", "MACKO", "MAGEN", "MAKIM", "MAKTK", "MANAS",
    "MARBL", "MARKA", "MARMR", "MARTI", "MAVI", "MCARD", "MEDTR", "MEGAP",
    "MEGMT", "MEKAG", "MEPET", "MERCN", "MERIT", "MERKO", "METRO", "MEYSU",
    "MGROS", "MHRGY", "MIATK", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MOGAN",
    "MOPAS", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD",
    "NATEN", "NETAS", "NETCD", "NIBAS", "NPTLR", "NTGAZ", "NTHOL", "NUGYO",
    "NUHCM", "OBAMS", "OBASE", "ODAS", "ODINE", "OFSYM", "ONCSM", "ONRYT",
    "ORCAY", "ORGE", "ORMA", "OSMEN", "OSTIM", "OTKAR", "OTTO", "OYAKC",
    "OYAYO", "OYLUM", "OYYAT", "OZATD", "OZGYO", "OZKGY", "OZRDN", "OZSUB",
    "OZYSR", "PAGYO", "PAHOL", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATE",
    "PEGYO", "PEKGY", "PENGD", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU",
    "PKART", "PKENT", "PLTUR", "PLUTO", "PMGYO", "PNLSN", "PNSUT", "POGRP",
    "POLHO", "POLTK", "PRDGM", "PRKAB", "PRKME", "PROFN", "PRZMA", "PSDMC",
    "PSGYO", "QUAGR", "RBNSY", "REEDR", "RGYAS", "RNPOL", "RODRG", "ROYAL",
    "RTAIB", "RTALB", "RUBNS", "SABAN", "SADAT", "SAFKR", "SAHOL", "SALMO",
    "SAMAT", "SANEL", "SANFM", "SANKO", "SAYAS", "SBAGB", "SBSGY", "SEGMN",
    "SEKFK", "SEKUR", "SELEC", "SEYKM", "SILVR", "SİRKEL", "SISE", "SKBNK",
    "SKTAS", "SKYLP", "SMART", "SMRTG", "SNGYO", "SNICA", "SNKRN", "SNPAM",
    "SOKM", "SONME", "SORTE", "SÖZBR", "SPORT", "SRVGY", "SSKBN", "STARH",
    "STDGY", "STFTT", "STRCMA", "SUDEN", "SUKGY", "SUNTK", "SURHL", "SUVGY",
    "TABGD", "TAVHL", "TCELL", "TDGYO", "TEKST", "TEKTU", "TERA", "TGSAS",
    "THYAO", "TIBMA", "TKFEN", "TKNSA", "TMPOL", "TMSN", "TMXTR", "TOASO",
    "TRCAS", "TRILC", "TSKCB", "TSKRS", "TSPOR", "TTKOM", "TTRAK", "TUCLK",
    "TUKAS", "TUPRS", "TUREX", "TURGG", "TURKL", "TUTAP", "TÜRKP", "UFUK",
    "UKGYO", "ULAS", "ULKER", "ULUFA", "ULUSE", "UMPAS", "UNBIS", "UNLMA",
    "UNLU", "UNTAR", "URAN", "URCEK", "USAK", "UYUM", "UZERB", "VAKBN",
    "VAKFN", "VANGD", "VBTSY", "VERTU", "VESBE", "VESTL", "VKGYO", "VRGYO",
    "YAPRK", "YATAS", "YAYLA", "YAZIC", "YBTAS", "YEGYO", "YEOTK", "YESIL",
    "YETMG", "YGGYO", "YIGIT", "YONGA", "YUNSA", "YYAPI", "ZEDUR", "ZOREN",
    # ETF ve endeksler
    "APBDL", "APGLD", "APLIB", "APMDL", "APX30", "BPIOM", "BPJST",
    "BPLIB", "BPM25", "BPM30", "BPS30", "BPSDL", "BPSPI", "BPXTU",
    "DBM25", "DBSPI", "DIBRY", "DVERT", "DZPBT", "GMBRY", "GMSBR",
    "GMSFT", "GMSTR", "GMTAH", "GMTCH", "GMTDT", "GMTFR", "GMSER",
    "IKTMC", "IPB27", "IPB30", "IPB50", "IPO24", "IPX30", "IPX50",
    "IPZ25", "IST30", "IZB27", "IZB30", "IZB50", "IZB70", "IZC25",
    "IZD30", "IZG25", "IZH25", "IZK25", "IZM25", "IZT25", "IZY30",
    "KCH25", "KCM30", "KSM25", "KSX30", "KTB27", "KTB30", "KTB70",
    "KTG25", "KTH25", "KTM30", "KTS25", "OPK30", "OPT25", "OPTGY",
    "OPTLR", "OPX30", "PASBJ", "PASJN", "PASKY", "PASMC", "PASMN",
    "PASSK", "PASTP", "PASYB", "PASYL", "PASYS", "PBDGP", "PBPJN",
    "PBSTM", "PEGAC", "PEGAP", "PEGAZ", "PEGLC", "PEGLD", "PEGM7",
    "PEGMC", "PEGMD", "PEGMO", "PEGP2", "PEGP3", "PEGPM", "PEGPZ",
    "PEGS6", "PEGS7", "PEGSC", "PEGSD", "PEGS8", "PEGS9", "PEGSA",
    "PEGSB", "PEGSE", "PEGSF", "PEGSG", "PEGSH", "PEGSJ", "PEGSK",
    "PEGSL", "PEGSM", "PEGSN", "PEGSO", "PEGSP", "PEGSR", "PEGSS",
    "PEGST", "PEGSU", "PEGSZ", "PEGT8", "PEGTA", "PEGTB", "PEGTC",
    "PEGTD", "PEGTE", "PEGTF", "PEGTG", "PEGTH", "PEGTI", "PEGTJ",
    "PEGTK", "PEGTL", "PEGTM", "PEGTN", "PEGTO", "PEGTP", "PEGTR",
    "PEGTS", "PEGTT", "PEGTU", "PEGTZ", "PEGYLD", "PEPJN", "PEPJST",
    "PEPMC", "PEPMN", "PEPST", "PEPTB", "PKGAC", "PKGAP", "PKGAZ",
    "PKGLC", "PKGLD", "PKGMT", "PKGMC", "PKGMD", "PKGMO", "PKGS6",
    "PKGSA", "PKGSB", "PKGSC", "PKGSD", "PKGSE", "PKGSG", "PKGSH",
    "PKGSJ", "PKGSK", "PKGSL", "PKGSM", "PKGSN", "PKGSO", "PKGSP",
    "PKGSR", "PKGSS", "PKGST", "PKGSU", "PKGTA", "PKGTB", "PKGTC",
    "PKGTD", "PKGTE", "PKGTF", "PKGTG", "PKGTH", "PKGTI", "PKGTJ",
    "PKGTK", "PKGTL", "PKGTM", "PKGTN", "PKGTO", "PKGTP", "PKGTR",
    "PKGTS", "PKGTT", "PKGTU", "PKGYLD", "PKSAP", "PKSCF", "PKSDT",
    "PKSEN", "PKSGT", "PKSHL", "PKSRD", "PKSTM", "PKSYD", "PKSYL",
    "PKSYP", "PKSYY", "PKSYZ", "PKSZD", "PKSZP", "PLIBP", "PMP25",
    "PMP30", "PMS30", "PMSDL", "PMSPI", "PMXTU", "PPX30", "PSDBC",
    "PSDBP", "PSDBS", "PSDBT", "PSIBB", "PSS25", "PSS30", "PSSAL",
    "PSSDL", "PSSPI", "PSTDM", "PSTDP", "PSTDT", "PSTDV", "PSX30",
    "PTL25", "PTL30", "PTL70", "PTX25", "PTX30", "PTX50", "PUBOP",
    "PVD25", "PVX25", "PVX30", "PXD25", "PXD30", "PYT25", "PYT30",
    "PYX30", "PZP25", "PZP30", "QNBST", "QNBVB", "QUGRP", "SBM25",
    "SBM30", "SBV25", "SBV30", "SBV70", "SBX30", "SBX50", "SFY25",
    "SFY30", "SGG25", "SGG30", "SGT25", "SGY25", "SHB30", "SKM25",
    "SKZ25", "SKZ30", "SMX25", "SMX30", "SMX50", "SPX25", "SPX30",
    "SSK30", "SST25", "STD30", "TAH25", "TCH25", "TCM25", "TDV25",
    "TEGM7", "TEGMC", "TEGMD", "TEGMO", "TEGP2", "TEGP3", "TEGPM",
    "TEGPZ", "TEGS6", "TEGS7", "TEGS8", "TEGS9", "TEGSA", "TEGSC",
    "TEGSD", "TEGSE", "TEGSF", "TEGSG", "TEGSH", "TEGSJ", "TEGSK",
    "TEGSL", "TEGSM", "TEGSN", "TEGSO", "TEGSP", "TEGSR", "TEGSS",
    "TEGST", "TEGSU", "TEGTA", "TEGTD", "TEGTE", "TEGTF", "TEGTG",
    "TEGTH", "TEGTI", "TEGTJ", "TEGTK", "TEGTL", "TEGTN", "TEGTO",
    "TEGTP", "TEGTR", "TEGTS", "TEGTT", "TEK25", "TEK30", "TEKHOL",
    "TGAH25", "TGAH30", "TGB25", "TGB30", "TGH25", "TGH30", "THM25",
    "THY30", "TIB25", "TIB30", "TIH25", "TIH30", "TJK25", "TJK30",
    "TJM25", "TJM30", "TKH25", "TKM25", "TKR30", "TKS25", "TKY25",
    "TKY30", "TMG30", "TMH25", "TMM25", "TMM30", "TMX30", "TMX50",
    "TNZ25", "TOC25", "TOC30", "TOF30", "TOM25", "TOV25", "TPD30",
    "TPJ30", "TPM25", "TPS25", "TPS30", "TPX25", "TPX30", "TPX50",
    "TPY25", "TRE25", "TRE30", "TRJ25", "TRJ30", "TRK25", "TRK30",
    "TRM25", "TRM30", "TRS25", "TRS30", "TRT25", "TRY30", "TSM25",
    "TTF30", "TUH25", "TUH30", "TUJ25", "TUJ30", "TUS30", "TUT30",
    "TUV30", "TVF25", "TVF30", "TVK25", "TVS25", "TVS30", "TYK30",
    "TYM25", "TYM30", "TYS30", "UCM30", "UKM25", "UKM30", "UPX25",
    "UPX30", "UYS30", "UZP25", "VDE25", "VDE30", "VDJ30", "VDM25",
    "VDM30", "VGI25", "VGI30", "VHS25", "VIT25", "VKD25", "VKD30",
    "VKG25", "VKM25", "VKS25", "VKSM", "VKY30", "VMH25", "VMH30",
    "VMI25", "VMI30", "VMJ30", "VML30", "VMSD", "VMT25", "VMT30",
    "VMX25", "VMX30", "VMX50", "VMY30", "VNI25", "VNR25", "VPM30",
    "VRD25", "VRD30", "VRG25", "VRG30", "VRM25", "VRS25", "VRS30",
    "VRT25", "VRT30", "VSD25", "VSM25", "VST25", "VST30", "VTA25",
    "VTD30", "VTJ30", "VTM25", "VTM30", "VTU30", "VTY25", "VTY30",
    "VYA25", "VYA30", "VYD30", "VYG25", "VYG30", "VYK30", "VYN25",
    "VYN30", "VYS30", "VYT30", "YTK25", "YTR30", "YYI25", "YYI30",
    "ZP25", "ZP30", "ZPA25", "ZPA30", "ZPD25", "ZPD30", "ZPJ25",
    "ZPJ30", "ZPK25", "ZPK30", "ZPM25", "ZPM30", "ZPO25", "ZPO30",
    "ZPS25", "ZPT10", "ZPT25", "ZPT30", "ZPY25", "ZPY30",
]

def test_ticker(symbol: str) -> bool:
    """Bir hissenin Yahoo Finance'de olup olmadigini test et."""
    try:
        ticker = yf.Ticker(f"{symbol}.IS")
        info = ticker.info
        if info and info.get("regularMarketPrice") is not None:
            return True
        return False
    except:
        return False

def main():
    print("=" * 60)
    print("BIST Tum Hisseleri Yahoo Finance'de Taniyor")
    print("=" * 60)
    
    found = []
    not_found = []
    
    for i, symbol in enumerate(BIST_ALL):
        exists = test_ticker(symbol)
        if exists:
            found.append(symbol)
            print(f"  [{i+1}/{len(BIST_ALL)}] {symbol}.IS -> VAR")
        else:
            not_found.append(symbol)
            print(f"  [{i+1}/{len(BIST_ALL)}] {symbol}.IS -> YOK")
        
        # Rate limiting
        if (i + 1) % 20 == 0:
            time.sleep(1)
    
    print(f"\nBulunan: {len(found)}")
    print(f"Bulunamayan: {len(not_found)}")
    
    # Python listesi olarak kaydet
    with open("bist_symbols_found.py", "w", encoding="utf-8") as f:
        f.write("# BIST Yahoo Finance'de bulunan hisseler\n")
        f.write(f"# Toplam: {len(found)}\n")
        f.write(f"BIST_SYMBOLS = {json.dumps(found, indent=4)}\n")
    
    print(f"\n[OK] bist_symbols_found.py kaydedildi ({len(found)} hisse)")

if __name__ == "__main__":
    main()
