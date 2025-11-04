import traceback

try:
    import scrapers.scraper_sistema_a_xls as a
    print('imported scrapers.scraper_sistema_a_xls, has main:', hasattr(a,'main'))
except Exception as e:
    print('FAILED import scrapers.scraper_sistema_a_xls')
    traceback.print_exc()

try:
    import scraper_sistema_a_xls as b
    print('imported scraper_sistema_a_xls, has main:', hasattr(b,'main'))
except Exception as e:
    print('FAILED import scraper_sistema_a_xls')
    traceback.print_exc()
