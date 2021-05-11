from datetime import datetime, timedelta


def daterange(start_date, end_date):
    start_date = datetime.strptime(str(start_date), '%Y%m%d')
    end_date = datetime.strptime(str(end_date), '%Y%m%d')
    for n in range(int((end_date - start_date).days)+1):
        yield (start_date + timedelta(n)).strftime('%Y%m%d')
