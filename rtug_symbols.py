"""
RTUG SYMBOLS — Master symbol database
Tüm piyasalardaki sembol listelerini içerir.
===================================================
BIST: 588 hisse
US:   S&P 500 ~503 hisse
World: FTSE 100, DAX 40, Nikkei 225, CAC 40, SMI 20, etc.
Crypto: Binance USDT 448 pair
"""

# ═══════════════════════════════════════════════════════════
# BIST (Borsa İstanbul) — tüm hisseler
# Kaynak: Borsa Istanbul resmi verisi (Temmuz 2026)
# ═══════════════════════════════════════════════════════════
BIST_SYMBOLS = [
    "A1CAP.IS", "A1YEN.IS", "AAGYO.IS", "ACSEL.IS", "ADEL.IS",
    "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS",
    "AGHOL.IS", "AGROT.IS", "AGYO.IS", "AHGAZ.IS", "AHSGY.IS",
    "AKBNK.IS", "AKCNS.IS", "AKENR.IS", "AKFGY.IS", "AKFIS.IS",
    "AKFYE.IS", "AKGRT.IS", "AKHAN.IS", "AKMGY.IS", "AKSA.IS",
    "AKSEN.IS", "AKSGY.IS", "AKSUE.IS", "AKYHO.IS", "ALARK.IS",
    "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALGYO.IS",
    "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALTNY.IS", "ALVES.IS",
    "ANELE.IS", "ANGEN.IS", "ANHYT.IS", "ANSGR.IS", "ARASE.IS",
    "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARFYE.IS", "ARMGD.IS",
    "ARSAN.IS", "ARTMS.IS", "ARZUM.IS", "ASELS.IS", "ASGYO.IS",
    "ASTOR.IS", "ASUZU.IS", "ATAGY.IS", "ATAKP.IS", "ATATP.IS",
    "ATATR.IS", "ATEKS.IS", "ATLAS.IS", "ATSYH.IS", "AVGYO.IS",
    "AVHOL.IS", "AVOD.IS", "AVPGY.IS", "AVTUR.IS", "AYCES.IS",
    "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS",
    "BAGFS.IS", "BAHKM.IS", "BAKAB.IS", "BALAT.IS", "BALSU.IS",
    "BANVT.IS", "BARMA.IS", "BASCM.IS", "BASGZ.IS", "BAYRK.IS",
    "BEGYO.IS", "BERA.IS", "BESLR.IS", "BESTE.IS", "BETAE.IS",
    "BEYAZ.IS", "BFREN.IS", "BIENY.IS", "BIGCH.IS", "BIGEN.IS",
    "BIGTK.IS", "BIMAS.IS", "BINBN.IS", "BINHO.IS", "BIOEN.IS",
    "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", "BLUME.IS", "BMSCH.IS",
    "BMSTL.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BORSK.IS",
    "BOSSA.IS", "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRKVY.IS",
    "BRLSM.IS", "BRMEN.IS", "BRSAN.IS", "BRYAT.IS", "BSOKE.IS",
    "BTCIM.IS", "BUCIM.IS", "BULGS.IS", "BURCE.IS", "BURVA.IS",
    "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASA.IS", "CATES.IS",
    "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEMZY.IS",
    "CEOEM.IS", "CGCAM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS",
    "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS",
    "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS",
    "DCTTR.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS",
    "DESPC.IS", "DEVA.IS", "DGATE.IS", "DGGYO.IS", "DGNMO.IS",
    "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS",
    "DOCO.IS", "DOFER.IS", "DOFRB.IS", "DOGUB.IS", "DOHOL.IS",
    "DOKTA.IS", "DSTKF.IS", "DUNYH.IS", "DURDO.IS", "DURKN.IS",
    "DYOBY.IS", "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECOGR.IS",
    "ECZYT.IS", "EDATA.IS", "EDIP.IS", "EFOR.IS", "EGEEN.IS",
    "EGEGY.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS",
    "EKDMR.IS", "EKGYO.IS", "EKIM.IS", "EKOS.IS", "EKSUN.IS",
    "ELITE.IS", "EMKEL.IS", "EMPAE.IS", "ENDAE.IS", "ENERY.IS",
    "ENJSA.IS", "ENKAI.IS", "ENSRI.IS", "ENTRA.IS", "EPLAS.IS",
    "ERBOS.IS", "ERCB.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS",
    "ESCOM.IS", "ESEN.IS", "ETILR.IS", "ETYAT.IS", "EUKYO.IS",
    "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS", "FADE.IS",
    "FENER.IS", "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS",
    "FORTE.IS", "FRIGO.IS", "FRMPL.IS", "FROTO.IS", "FZLGY.IS",
    "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENIL.IS",
    "GENKM.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS", "GIPTA.IS",
    "GLBMD.IS", "GLCVY.IS", "GLRMK.IS", "GLRYH.IS", "GLYHO.IS",
    "GMTAS.IS", "GOKNR.IS", "GOLDA.IS", "GOLTS.IS", "GOODY.IS",
    "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GRTHO.IS", "GSDDE.IS",
    "GSDHO.IS", "GSRAY.IS", "GUBRF.IS", "GUNDG.IS", "GWIND.IS",
    "GZNMI.IS", "HALKB.IS", "HATEK.IS", "HATSN.IS", "HDFGS.IS",
    "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HOROZ.IS",
    "HRKET.IS", "HTTBT.IS", "HUBVC.IS", "HUNER.IS", "HURGZ.IS",
    "ICBCT.IS", "ICUGS.IS", "IDGYO.IS", "IEYHO.IS", "IHAAS.IS",
    "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IHYAY.IS",
    "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS", "INTEM.IS",
    "INVEO.IS", "INVES.IS", "ISATR.IS", "ISBTR.IS", "ISCTR.IS",
    "ISDMR.IS", "ISFIN.IS", "ISGSY.IS", "ISGYO.IS", "ISKPL.IS",
    "ISMEN.IS", "ISSEN.IS", "ISVEA.IS", "IZENR.IS", "IZFAS.IS",
    "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS", "KAREL.IS",
    "KARSN.IS", "KARTN.IS", "KATMR.IS", "KAYSE.IS", "KBORU.IS",
    "KCAER.IS", "KCHOL.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS",
    "KLGYO.IS", "KLKIM.IS", "KLMSN.IS", "KLRHO.IS", "KLSER.IS",
    "KLSYN.IS", "KLYPV.IS", "KMPUR.IS", "KNFRT.IS", "KOCMT.IS",
    "KONKA.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS",
    "KRDMA.IS", "KRDMB.IS", "KRDMD.IS", "KRGYO.IS", "KRONT.IS",
    "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KRVGD.IS", "KTLEV.IS",
    "KTSKR.IS", "KUTPO.IS", "KUVVA.IS", "KUYAS.IS", "KZBGY.IS",
    "KZGYO.IS", "LIDER.IS", "LIDFA.IS", "LILAK.IS", "LINK.IS",
    "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LRSHO.IS", "LUKSK.IS",
    "LXGYO.IS", "LYDHO.IS", "LYDYE.IS", "MAALT.IS", "MACKO.IS",
    "MAGEN.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARBL.IS",
    "MARKA.IS", "MARMR.IS", "MARTI.IS", "MAVI.IS", "MCARD.IS",
    "MEDTR.IS", "MEGMT.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS",
    "MERIT.IS", "MERKO.IS", "METRO.IS", "MEYSU.IS", "MGROS.IS",
    "MHRGY.IS", "MIATK.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS",
    "MOGAN.IS", "MOPAS.IS", "MPARK.IS", "MRGYO.IS", "MRSHL.IS",
    "MSGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS",
    "NETAS.IS", "NETCD.IS", "NIBAS.IS", "NTGAZ.IS", "NTHOL.IS",
    "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS",
    "ODINE.IS", "OFSYM.IS", "ONCSM.IS", "ONRYT.IS", "ORCAY.IS",
    "ORGE.IS", "ORZAX.IS", "OSMEN.IS", "OSTIM.IS", "OTKAR.IS",
    "OTTO.IS", "OYAKC.IS", "OYAYO.IS", "OYLUM.IS", "OYYAT.IS",
    "OZATD.IS", "OZGYO.IS", "OZKGY.IS", "OZRDN.IS", "OZSUB.IS",
    "OZYSR.IS", "PAGYO.IS", "PAHOL.IS", "PAMEL.IS", "PAPIL.IS",
    "PARSN.IS", "PASEU.IS", "PATEK.IS", "PCILT.IS", "PEKGY.IS",
    "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS",
    "PINSU.IS", "PKART.IS", "PKENT.IS", "PLTUR.IS", "PNLSN.IS",
    "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKAB.IS",
    "PRKME.IS", "PRZMA.IS", "PSDTC.IS", "PSGYO.IS", "QUAGR.IS",
    "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RGYAS.IS", "RNPOL.IS",
    "RODRG.IS", "RTALB.IS", "RUBNS.IS", "RUZYE.IS", "RYGYO.IS",
    "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SAMAT.IS", "SANEL.IS",
    "SANFM.IS", "SANKO.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS",
    "SDTTR.IS", "SEGMN.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS",
    "SELEC.IS", "SELVA.IS", "SERNT.IS", "SEYKM.IS", "SILVR.IS",
    "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SKYLP.IS", "SKYMD.IS",
    "SMART.IS", "SMRTG.IS", "SMRVA.IS", "SNGYO.IS", "SNICA.IS",
    "SOHOE.IS", "SOKE.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS",
    "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "SVGYO.IS", "TABGD.IS",
    "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS",
    "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEHOL.IS", "TEKTU.IS",
    "TERA.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS",
    "TKNSA.IS", "TLMAN.IS", "TMPOL.IS", "TMSN.IS", "TNZTP.IS",
    "TOASO.IS", "TRALT.IS", "TRCAS.IS", "TRENJ.IS", "TRGYO.IS",
    "TRHOL.IS", "TRMET.IS", "TSGYO.IS", "TSKB.IS", "TSPOR.IS",
    "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUKAS.IS", "TUPRS.IS",
    "TUREX.IS", "TURGG.IS", "TURSG.IS", "UCAYM.IS", "UFUK.IS",
    "ULAS.IS", "ULKER.IS", "ULUFA.IS", "ULUSE.IS", "ULUUN.IS",
    "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKFA.IS", "VAKFN.IS",
    "VAKKO.IS", "VANGD.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS",
    "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS",
    "VRGYO.IS", "VSNMD.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS",
    "YEOTK.IS", "YESIL.IS", "YGGYO.IS", "YIGIT.IS", "YKBNK.IS",
    "YKSLN.IS", "YUNSA.IS", "YYLGD.IS", "ZEDUR.IS", "ZERGY.IS",
    "ZGYO.IS", "ZOREN.IS", "ZRGYO.IS",
]

# ═══════════════════════════════════════════════════════════
# US — S&P 500 (Temmuz 2026)
# ═══════════════════════════════════════════════════════════
SP500_SYMBOLS = [
    "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL",
    "A", "APD", "ABNB", "AKAM", "ALB", "ARE", "ALGN", "ALLE", "LNT",
    "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AEP", "AXP",
    "AIG", "AMT", "AWK", "AMP", "AME", "AMGN", "APH", "ADI", "AON",
    "APA", "APO", "AAPL", "AMAT", "APP", "APTV", "ACGL", "ADM", "ARES",
    "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", "ADP", "AZO", "AVB",
    "AVY", "AXON", "BKR", "BALL", "BAC", "BAX", "BDX", "BRK.B", "BBY",
    "TECH", "BIIB", "BLK", "BX", "XYZ", "BNY", "BA", "BKNG", "BSX",
    "BMY", "AVGO", "BR", "BRO", "BF.B", "BLDR", "BG", "BXP", "CHRW",
    "CDNS", "CPT", "COF", "CAH", "CCL", "CARR", "CVNA", "CASY", "CAT",
    "CBOE", "CBRE", "CDW", "COR", "CNC", "CNP", "CF", "CRL", "SCHW",
    "CHTR", "CVX", "CMG", "CB", "CHD", "CIEN", "CI", "CINF", "CTAS",
    "CSCO", "C", "CFG", "CLX", "CME", "CMS", "KO", "CTSH", "COHR",
    "COIN", "CL", "CMCSA", "FIX", "COP", "ED", "STZ", "CEG", "COO",
    "CPRT", "GLW", "CPAY", "CTVA", "CSGP", "COST", "CRH", "CRWD",
    "CCI", "CSX", "CMI", "CVS", "DHR", "DRI", "DDOG", "DVA", "DECK",
    "DE", "DELL", "DAL", "DVN", "DXCM", "DEO", "FANG", "DLR", "DG",
    "DLTR", "D", "DPZ", "DASH", "DOV", "DOW", "DHI", "DTE", "DUK",
    "DD", "ETN", "EBAY", "ECHO", "ECL", "EIX", "EW", "EA", "ELV",
    "EME", "EMR", "ETR", "EOG", "EQT", "EFX", "EQIX", "EQR", "ERIE",
    "ESS", "EL", "EG", "EVRG", "ES", "EXC", "EXE", "EXPE", "EXPD",
    "EXR", "XOM", "FFIV", "FDS", "FICO", "FAST", "FRT", "FDX", "FDXF",
    "FIS", "FITB", "FSLR", "FE", "FISV", "FLEX", "F", "FTNT", "FTV",
    "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT", "GE", "GEHC", "GEV",
    "GEN", "GNRC", "GD", "GIS", "GM", "GPC", "GILD", "GPN", "GL",
    "GDDY", "GS", "HAL", "HIG", "HAS", "HCA", "DOC", "HSIC", "HSY",
    "HPE", "HLT", "HD", "HONA", "HON", "HRL", "HST", "HWM", "HPQ",
    "HUBB", "HUM", "HBAN", "HII", "IBM", "IEX", "IDXX", "ITW", "INCY",
    "IR", "PODD", "INTC", "IBKR", "ICE", "IFF", "IP", "INTU", "ISRG",
    "IVZ", "INVH", "IQV", "IRM", "JBHT", "JBL", "JKHY", "J", "JNJ",
    "JCI", "JPM", "KVUE", "KDP", "KEY", "KEYS", "KMB", "KIM", "KMI",
    "KKR", "KLAC", "KHC", "KR", "LHX", "LH", "LRCX", "LVS", "LDOS",
    "LEN", "LII", "LLY", "LIN", "LYV", "LMT", "L", "LOW", "LULU",
    "LITE", "LYB", "MTB", "MPC", "MAR", "MRSH", "MLM", "MRVL", "MAS",
    "MA", "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET", "MTD",
    "MGM", "MCHP", "MU", "MSFT", "MAA", "MRNA", "TAP", "MDLZ", "MPWR",
    "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP", "NFLX",
    "NEM", "NWSA", "NWS", "NEE", "NKE", "NI", "NDSN", "NSC", "NTRS",
    "NOC", "NCLH", "NRG", "NUE", "NVDA", "NVR", "NXPI", "ORLY", "OXY",
    "ODFL", "OMC", "ON", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PLTR",
    "PANW", "PSKY", "PH", "PAYX", "PYPL", "PNR", "PEP", "PFE", "PCG",
    "PM", "PSX", "PNW", "PNC", "PPG", "PPL", "PFG", "PG", "PGR",
    "PLD", "PRU", "PEG", "PTC", "PSA", "PHM", "PWR", "QCOM", "DGX",
    "Q", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD",
    "RVTY", "HOOD", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM",
    "SNDK", "SBAC", "SLB", "STX", "SRE", "NOW", "SHW", "SPG", "SWKS",
    "SJM", "SW", "SNA", "SOLV", "SO", "LUV", "SWK", "SBUX", "STT",
    "STLD", "STE", "SYK", "SMCI", "SYF", "SNPS", "SYY", "TMUS", "TROW",
    "TTWO", "TPR", "TRGP", "TGT", "TEL", "TDY", "TER", "TSLA", "TXN",
    "TPL", "TXT", "TMO", "TJX", "TKO", "TTD", "TSCO", "TT", "TDG",
    "TRV", "TRMB", "TFC", "TYL", "TSN", "USB", "UBER", "UDR", "ULTA",
    "UNP", "UAL", "UPS", "URI", "UNH", "UHS", "VLO", "VEEV", "VTR",
    "VLTO", "VRSN", "VRSK", "VZ", "VRTX", "VRT", "VTRS", "VICI", "V",
    "VST", "VMC", "WRB", "GWW", "WAB", "WMT", "WBA", "WM", "WAT",
    "WEC", "WFC", "WELL", "WST", "WDC", "WY", "WHR", "WWD", "WMB",
    "WYNN", "XEL", "XPO", "XYL", "YUM", "ZBRA", "ZBH", "ZTS",
]

# ═══════════════════════════════════════════════════════════
# DÜNYA BORSALARI — Majör endeksler
# ═══════════════════════════════════════════════════════════

# FTSE 100 (UK) + ek UK hisseleri
UK_SYMBOLS = [
    "ABF.L", "ADM.L", "AAL.L", "ANG.L", "ANTO.L", "AHT.L",
    "AZN.L", "BA.L", "BARC.L", "BDEV.L", "BKG.L", "BNZL.L",
    "BP.L", "BT-A.L", "BLND.L", "BME.L", "CNA.L", "CPG.L",
    "CRH.L", "CRDA.L", "DCC.L", "DGE.L", "EVR.L", "EXPN.L",
    "FCIT.L", "FLTR.L", "FRES.L", "GSK.L", "GLEN.L", "HAL.L",
    "HIK.L", "HL.L", "HLMA.L", "HSBA.L", "HWDN.L", "IAG.L",
    "IHG.L", "III.L", "IMB.L", "INF.L", "INT.L", "IQA.L",
    "ITRK.L", "JD.L", "JMAT.L", "KGF.L", "LAND.L", "LGEN.L",
    "LLOY.L", "LMP.L", "LSEG.L", "MNG.L", "MRO.L", "MNDI.L",
    "NG.L", "NXT.L", "OCDO.L", "PHNX.L", "POLY.L", "PRU.L",
    "PSN.L", "RB.L", "REL.L", "RTO.L", "RIO.L", "RR.L",
    "RSA.L", "SBRY.L", "SGE.L", "SGRO.L", "SHEL.L", "SDR.L",
    "SMT.L", "SMIN.L", "SN.L", "SPX.L", "SSE.L", "STAN.L",
    "STJ.L", "SVT.L", "TSCO.L", "TW.L", "ULVR.L", "UU.L",
    "VOD.L", "WEIR.L", "WPP.L",
]

# DAX 40 (Almanya)
GERMANY_SYMBOLS = [
    "ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE",
    "BNR.DE", "CBK.DE", "CON.DE", "DAI.DE", "DB1.DE", "DBK.DE",
    "DHL.DE", "DTE.DE", "DWNI.DE", "EOAN.DE", "FME.DE", "FRE.DE",
    "HEI.DE", "HEN3.DE", "HNR1.DE", "IFX.DE", "MRK.DE", "MTX.DE",
    "MUV2.DE", "PAH3.DE", "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE",
    "SIE.DE", "SY1.DE", "TKA.DE", "TUI.DE", "VOW3.DE", "VNA.DE",
    "ZAL.DE", "BOSS.DE", "PUM.DE", "LEG.DE",
]

# CAC 40 (Fransa)
FRANCE_SYMBOLS = [
    "AC.PA", "AI.PA", "AIR.PA", "ATO.PA", "BN.PA", "BNP.PA",
    "CA.PA", "CAP.PA", "CS.PA", "DG.PA", "DSY.PA", "EL.PA",
    "EN.PA", "ENGI.PA", "GLE.PA", "KER.PA", "LR.PA", "MC.PA",
    "ML.PA", "MMB.PA", "OR.PA", "PUB.PA", "RNO.PA", "SAF.PA",
    "SGO.PA", "SK.PA", "STMPA.PA", "SU.PA", "SW.PA", "SYM.PA",
    "TTE.PA", "UG.PA", "VIE.PA", "VIV.PA",
]

# Nikkei 225 (Japonya) — önemli olanlar
JAPAN_SYMBOLS = [
    "7203.T", "9984.T", "6861.T", "6758.T", "8035.T", "6098.T",
    "9432.T", "9433.T", "9434.T", "9437.T", "4502.T", "4503.T",
    "4578.T", "4523.T", "4543.T", "2914.T", "2502.T", "2503.T",
    "3382.T", "8267.T", "9843.T", "9983.T", "8058.T", "9101.T",
    "9104.T", "9107.T", "9201.T", "9202.T", "9501.T", "9502.T",
    "9503.T", "8306.T", "8316.T", "8411.T", "7186.T", "8604.T",
    "8766.T", "8725.T", "8630.T", "4503.T", "7751.T", "7731.T",
    "7733.T", "6701.T", "6702.T", "6723.T", "6971.T", "6976.T",
    "6954.T", "6981.T", "7004.T", "7011.T", "7012.T", "7013.T",
    "6501.T", "6502.T", "6503.T", "6506.T", "6479.T", "6361.T",
    "6367.T", "6273.T", "6301.T", "6302.T", "6305.T", "6326.T",
    "3401.T", "3402.T", "3405.T", "3407.T", "3861.T", "3863.T",
    "3865.T", "4004.T", "4005.T", "4021.T", "4041.T", "4042.T",
    "4043.T", "4061.T", "4062.T", "4063.T", "4091.T", "4151.T",
    "4183.T", "4188.T", "4202.T", "4208.T", "4452.T", "4521.T",
    "4901.T", "4902.T", "5001.T", "5002.T", "5101.T", "5105.T",
    "5108.T", "5110.T", "5201.T", "5202.T", "5210.T", "5232.T",
    "5233.T", "5301.T", "5332.T", "5333.T", "5401.T", "5406.T",
    "5411.T", "5541.T", "5631.T", "5703.T", "5706.T", "5711.T",
    "5713.T", "5714.T", "5715.T", "5801.T", "5802.T", "5803.T",
    "5901.T", "5902.T", "5938.T", "5947.T", "5991.T", "6013.T",
    "6028.T", "6030.T", "6031.T", "6035.T", "6103.T", "6113.T",
    "6134.T", "6135.T", "6141.T", "6143.T", "6146.T", "6165.T",
    "6201.T", "6222.T", "6240.T", "6269.T", "6278.T", "6282.T",
    "6284.T", "6287.T", "6291.T", "6323.T", "6325.T", "6345.T",
    "6349.T", "6351.T", "6361.T", "6366.T", "6368.T", "6370.T",
    "6383.T", "6395.T", "6407.T", "6412.T", "6417.T", "6420.T",
    "6444.T", "6448.T", "6457.T", "6460.T", "6471.T", "6472.T",
    "6473.T", "6479.T", "6480.T", "6481.T", "6482.T", "6485.T",
    "6486.T", "6488.T", "6498.T", "6501.T", "6502.T", "6504.T",
    "6506.T", "6508.T", "6513.T", "6516.T", "6517.T", "6518.T",
    "6525.T", "6526.T", "6584.T", "6586.T", "6588.T", "6590.T",
    "6592.T", "6594.T", "6601.T", "6620.T", "6623.T", "6632.T",
    "6641.T", "6645.T", "6651.T", "6662.T", "6670.T", "6674.T",
    "6675.T", "6701.T", "6702.T", "6703.T", "6704.T", "6706.T",
    "6707.T", "6709.T", "6715.T", "6718.T", "6721.T", "6723.T",
    "6724.T", "6727.T", "6728.T", "6737.T", "6740.T", "6741.T",
    "6742.T", "6744.T", "6750.T", "6752.T", "6753.T", "6754.T",
    "6755.T", "6758.T", "6762.T", "6767.T", "6770.T", "6773.T",
    "6775.T", "6787.T", "6791.T", "6794.T", "6796.T", "6798.T",
    "6804.T", "6806.T", "6807.T", "6809.T", "6810.T", "6815.T",
    "6816.T", "6817.T", "6841.T", "6845.T", "6849.T", "6850.T",
    "6856.T", "6857.T", "6858.T", "6861.T", "6862.T", "6863.T",
    "6866.T", "6869.T", "6870.T", "6871.T", "6875.T", "6877.T",
    "6879.T", "6890.T", "6902.T", "6905.T", "6911.T", "6914.T",
    "6915.T", "6920.T", "6923.T", "6925.T", "6927.T", "6928.T",
    "6929.T", "6937.T", "6941.T", "6947.T", "6951.T", "6952.T",
    "6954.T", "6955.T", "6958.T", "6960.T", "6961.T", "6962.T",
    "6963.T", "6965.T", "6966.T", "6967.T", "6971.T", "6976.T",
    "6981.T", "6986.T", "6988.T", "6995.T", "6997.T", "6999.T",
    "7003.T", "7004.T", "7011.T", "7012.T", "7013.T", "7014.T",
]

# Hang Seng (Hong Kong) — önemli hisseler
HK_SYMBOLS = [
    "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK",
    "0011.HK", "0012.HK", "0016.HK", "0017.HK", "0019.HK",
    "0027.HK", "0066.HK", "0083.HK", "0101.HK", "0175.HK",
    "0241.HK", "0267.HK", "0288.HK", "0293.HK", "0316.HK",
    "0388.HK", "0669.HK", "0688.HK", "0700.HK", "0762.HK",
    "0823.HK", "0857.HK", "0883.HK", "0939.HK", "0941.HK",
    "0960.HK", "0981.HK", "0992.HK", "1044.HK", "1088.HK",
    "1093.HK", "1109.HK", "1113.HK", "1299.HK", "1398.HK",
    "1928.HK", "1997.HK", "2018.HK", "2269.HK", "2318.HK",
    "2319.HK", "2388.HK", "2382.HK", "2628.HK", "2800.HK",
    "2822.HK", "2823.HK", "2828.HK", "3328.HK", "3690.HK",
    "3968.HK", "3988.HK", "6186.HK", "6862.HK", "82318.HK",
    "82822.HK", "82828.HK", "82823.HK", "82828.HK",
]

# ASX 50 (Avustralya)
AUSTRALIA_SYMBOLS = [
    "ANZ.AX", "AMP.AX", "ALL.AX", "AGL.AX", "BHP.AX", "BXB.AX",
    "CBA.AX", "COL.AX", "COH.AX", "CPU.AX", "CSL.AX", "DXS.AX",
    "FMG.AX", "GMG.AX", "IAG.AX", "JHX.AX", "MGR.AX", "MQG.AX",
    "NAB.AX", "ORI.AX", "QBE.AX", "RHC.AX", "RIO.AX", "SCG.AX",
    "SGP.AX", "STO.AX", "SUN.AX", "TCL.AX", "TLS.AX", "WBC.AX",
    "WES.AX", "WOW.AX", "WPL.AX", "XRO.AX",
]

# ═══════════════════════════════════════════════════════════
# KRİPTO — Binance USDT pair'leri (canlı çekilir)
# ═══════════════════════════════════════════════════════════

def get_all_crypto_symbols():
    """Binance'den tüm aktif USDT pair'lerini al."""
    try:
        import ccxt
        exchange = ccxt.binance({'enableRateLimit': True})
        markets = exchange.load_markets()
        pairs = [s for s in markets if s.endswith('/USDT') and markets[s].get('active')]
        return sorted(pairs)
    except Exception as e:
        print(f"⚠️ Kripto sembolleri alınamadı: {e}")
        return []

# ═══════════════════════════════════════════════════════════
# TÜM SEMBOLLER (birleşik)
# ═══════════════════════════════════════════════════════════

def get_all_stock_symbols():
    """Tüm hisse senetlerini döndür (BIST + SP500 + Dünya)."""
    all_stocks = []
    all_stocks.extend(BIST_SYMBOLS)
    all_stocks.extend(SP500_SYMBOLS)
    all_stocks.extend(UK_SYMBOLS)
    all_stocks.extend(GERMANY_SYMBOLS)
    all_stocks.extend(FRANCE_SYMBOLS)
    all_stocks.extend(JAPAN_SYMBOLS)
    all_stocks.extend(HK_SYMBOLS)
    all_stocks.extend(AUSTRALIA_SYMBOLS)
    return all_stocks


def get_market_name(symbol: str) -> str:
    """Sembolün hangi piyasaya ait olduğunu döndür."""
    if symbol.endswith(".IS"):
        return "BIST"
    elif symbol.endswith(".L"):
        return "UK"
    elif symbol.endswith(".DE"):
        return "Almanya"
    elif symbol.endswith(".PA"):
        return "Fransa"
    elif symbol.endswith(".T"):
        return "Japonya"
    elif symbol.endswith(".HK"):
        return "Hong Kong"
    elif symbol.endswith(".AX"):
        return "Avustralya"
    elif symbol.endswith("/USDT"):
        return "Kripto"
    elif symbol.upper() == symbol and not any(suffix in symbol for suffix in [".", "/"]):
        return "US"
    else:
        return "Diğer"


def get_yahoo_periods(symbol: str):
    """Hisse tipine göre uygun Yahoo Finance period döndür."""
    if symbol.endswith(".IS"):
        return "6mo", "1d"  # BIST
    elif symbol.endswith((".L", ".DE", ".PA", ".T", ".HK", ".AX")):
        return "6mo", "1d"  # Yabancı hisseler
    else:
        return "6mo", "1d"  # US


if __name__ == "__main__":
    stocks = get_all_stock_symbols()
    crypto = get_all_crypto_symbols()
    print(f"📊 Hisse senedi sembolleri: {len(stocks)}")
    print(f"   BIST: {len(BIST_SYMBOLS)}")
    print(f"   S&P 500: {len(SP500_SYMBOLS)}")
    print(f"   UK: {len(UK_SYMBOLS)}")
    print(f"   Almanya: {len(GERMANY_SYMBOLS)}")
    print(f"   Fransa: {len(FRANCE_SYMBOLS)}")
    print(f"   Japonya: {len(JAPAN_SYMBOLS)}")
    print(f"   Hong Kong: {len(HK_SYMBOLS)}")
    print(f"   Avustralya: {len(AUSTRALIA_SYMBOLS)}")
    print(f"₿ Kripto sembolleri: {len(crypto)}")
    print(f"📈 TOPLAM: {len(stocks) + len(crypto)}")
