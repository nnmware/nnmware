import xml.dom.minidom as xm
import requests
import zipfile
from glob import glob

# Full
URL_UPDATE = 'http://fias.nalog.ru/Public/Downloads/Actual/fias_xml.zip'
FILE_UPDATE = 'fias_xml.zip'
# Update
#URL_UPDATE = 'http://fias.nalog.ru/Public/Downloads/Actual/fias_delta_xml.zip'
#FILE_UPDATE = 'fias_delta_xml.zip'



def get_fias_delta_xml(url, file):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f'OK get: {file}')


def unpack_file(file):
    with open(file, 'rb') as zf:
        z = zipfile.ZipFile(zf, allowZip64=True)
        for fl in z.infolist():
            try:
                z.extract(fl)
                print(f'Decompressing ZIP file {fl} - OK')
            except zipfile.error as err:
                print(f'ERROR decompressing ZIP file: {err}')


def address_object_type():
    """
    Тип адресного объекта:
    LEVEL - Уровень адресного объекта
    SCNAME - Краткое наименование типа объекта
    SOCRNAME - Полное наименование типа объекта
    KOD_T_ST - Ключевое поле
    :return:
  """
    fl = glob('AS_SOCRBASE_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('AddressObjectType')
    print(f'===  Тип адресного объекта  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("LEVEL")] = [attr.getAttribute("SOCRNAME"), attr.getAttribute("SCNAME"), attr.getAttribute("KOD_T_ST")]
        print(f'{attr.getAttribute("LEVEL")} - {attr.getAttribute("SOCRNAME")} - {attr.getAttribute("SCNAME")} - {attr.getAttribute("KOD_T_ST")}')
    # return data

def structure_status():
    """
    Признак строения:
    STRSTATID - Признак строения
    NAME - Наименование
    SHORTNAME - Краткое наименование
    :return:
    """
    fl = glob('AS_STRSTAT_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('StructureStatus')
    print(f'===  Признак строения  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("STRSTATID")] = [attr.getAttribute("NAME"), attr.getAttribute("SHORTNAME")]
        print(f'{attr.getAttribute("STRSTATID")} - {attr.getAttribute("NAME")} - {attr.getAttribute("SHORTNAME")} - {attr.getAttribute("KOD_T_ST")}')
    # return data


def room_type():
    """
    Тип комнаты:
    RMTYPEID - Тип комнаты
    NAME - Наименование
    SHORTNAME - Краткое наименование
    :return:
    """
    fl = glob('AS_ROOMTYPE_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('RoomType')
    print(f'===  Тип комнаты  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("RMTYPEID")] = [attr.getAttribute("NAME"), attr.getAttribute("SHORTNAME")]
        print(f'{attr.getAttribute("RMTYPEID")} - {attr.getAttribute("NAME")} - {attr.getAttribute("SHORTNAME")}')
    # return data


def estate_status():
    """
    Признак владения:
    ESTSTATID - Признак владения
    NAME - Наименование
    SHORTNAME - Краткое наименование
    :return:
    """
    fl = glob('AS_ESTSTAT_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('EstateStatus')
    print(f'===  Признак владения  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("ESTSTATID")] = [attr.getAttribute("NAME"), attr.getAttribute("SHORTNAME")]
        print(f'{attr.getAttribute("ESTSTATID")} - {attr.getAttribute("NAME")} - {attr.getAttribute("SHORTNAME")}')
    # return data

def flat_type():
    """
    Тип помещения:
    FLTYPEID - Тип помещения
    NAME - Наименование
    SHORTNAME - Краткое наименование
    :return:
    """
    fl = glob('AS_FLATTYPE_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('FlatType')
    print(f'===  Тип помещения  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("FLTYPEID")] = [attr.getAttribute("NAME"), attr.getAttribute("SHORTNAME")]
        print(f'{attr.getAttribute("FLTYPEID")} - {attr.getAttribute("NAME")} - {attr.getAttribute("SHORTNAME")}')
    # return data


def room():
    """
    Классификатор помещениях (берем основные):
    FLATNUMBER - Номер помещения или офиса
    FLATTYPE - Тип помещения
    ROOMNUMBER - Номер комнаты
    ROOMTYPE - Тип комнаты
    POSTALCODE - Почтовый индекс
    HOUSEGUID - Идентификатор родительского объекта (дома)
    :return:
    """
    fl = glob('AS_ROOM_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('Room')
    print(f'===  Классификатор помещениях  ===')
    # data = []
    for attr in elem:
        # d = {}
        # d['HOUSEGUID'] = attr.getAttribute("HOUSEGUID")
        # d['NAME'] = attr.getAttribute("NAME")
        # d['SHORTNAME'] = attr.getAttribute("SHORTNAME")
        # data.append(d)
        # data[attr.getAttribute("HOUSEGUID")] = [attr.getAttribute("NAME"), attr.getAttribute("SHORTNAME")]
        print(f'{attr.getAttribute("HOUSEGUID")} - {attr.getAttribute("POSTALCODE")} - {attr.getAttribute("FLATNUMBER")} - {ft[attr.getAttribute("FLATTYPE")]} - {attr.getAttribute("ROOMNUMBER")} - {rt[attr.getAttribute("ROOMTYPE")]}')
    # return data


def house():
    """
    Классификатор помещениях (берем основные):
    HOUSENUM - Номер дома
    ESTSTATUS - Признак владения
    BUILDNUM - Номер корпуса
    STRUCNUM - Номер строения
    STRSTATUS - Признак строения
    HOUSEID - Уникальный идентификатор записи дома
    POSTALCODE - Почтовый индекс
    HOUSEGUID - Глобальный уникальный идентификатор дома
    AOGUID - Guid записи родительского объекта (улицы, города, населенного пункта и т.п.)
    :return:
    """
    fl = glob('AS_HOUSE_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('House')
    print(f'===  Классификатор помещениях  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("HOUSEGUID")] = [attr.getAttribute("ESTSTATUS"), attr.getAttribute("BUILDNUM"),
        #                                        attr.getAttribute("STRUCNUM"), attr.getAttribute("STRSTATUS"),
        #                                        attr.getAttribute("HOUSEID"), attr.getAttribute("HOUSENUM"),
        #                                        attr.getAttribute("AOGUID")]
        print(f'{attr.getAttribute("HOUSEGUID")} - {attr.getAttribute("POSTALCODE")} - {attr.getAttribute("FLATNUMBER")} - {ft[attr.getAttribute("FLATTYPE")]} - {attr.getAttribute("ROOMNUMBER")} - {rt[attr.getAttribute("ROOMTYPE")]}')
    # return data


def objects():
    """
    AOGUID - Guid записи родительского объекта (улицы, города, населенного пункта и т.п.)
    :return:
    """
    fl = glob('AS_ADDROBJ_*')[0]
    doc = xm.parse(fl)
    elem = doc.getElementsByTagName('Object')
    print(f'===  Классификатор помещениях  ===')
    # data = {}
    for attr in elem:
        # data[attr.getAttribute("AOGUID")] = [attr.getAttribute("FORMALNAME"), attr.getAttribute("STREETCODE"),
        #                                        attr.getAttribute("OFFNAME")]
        print(f'{attr.getAttribute("HOUSEGUID")} - {attr.getAttribute("POSTALCODE")} - {attr.getAttribute("FLATNUMBER")} - {ft[attr.getAttribute("FLATTYPE")]} - {attr.getAttribute("ROOMNUMBER")} - {rt[attr.getAttribute("ROOMTYPE")]}')
    # return data


if __name__ == '__main__':
    #get_fias_delta_xml(URL_UPDATE, FILE_UPDATE)
    unpack_file(FILE_UPDATE)
    #address_object_type()
    #room_type()
    #estate_status()
    #flat_type()
    #structure_status()
    # rm = room()
    # hs = house()
    # print(f'house: {len(hs)}')
    # ob = objects()
    # x = 0
    # print(f'object: {len(ob)}')
    # for i in hs.keys():
    #     hguid = hs[i][-1]
    #     h = ob.get(hguid)
    #     if h:
    #         r = hs[i]
    #         # print(f'{r}')
    #         print(f'HOUSENUM: {hs[i][5]} - OFFNAME: {h[0]}')
    #     x += 1
    #     if x == 100:
    #         print('break')
    #         break
    # for i in ob.keys():
    #     print(ob[i])
    #     x += 1
    #     if x == 100:
    #         break



'''
AS_ADDROBJ_*.xml

<Object AOID="d2fe86f7-5cb6-4be0-acf7-e0290fceccb6" AOGUID="026f0d19-ffcf-448e-bc5c-06d31f911eea" PARENTGUID="4660c67b-388d-41f9-a440-79f58de4d73d" PREVID="40911669-e66c-411e-b356-e872fed61b85" NEXTID="aacfe460-ffb4-4556-9bc7-4f42aa96e1ab" FORMALNAME="Береговая" OFFNAME="Береговая" SHORTNAME="ул" AOLEVEL="7" REGIONCODE="70" AREACODE="003" AUTOCODE="0" CITYCODE="000" CTARCODE="000" PLACECODE="010" PLANCODE="0000" STREETCODE="0002" EXTRCODE="0000" SEXTCODE="000" PLAINCODE="700030000100002" CODE="70003000010000202" CURRSTATUS="2" ACTSTATUS="0" LIVESTATUS="0" CENTSTATUS="0" OPERSTATUS="21" IFNSFL="7025" IFNSUL="7025" TERRIFNSFL="7002" TERRIFNSUL="7002" OKATO="69208810006" OKTMO="69608410111" POSTALCODE="636843" STARTDATE="2014-01-10" ENDDATE="2017-03-01" UPDATEDATE="2020-11-29" DIVTYPE="0" />

AOID="d2fe86f7-5cb6-4be0-acf7-e0290fceccb6"  -  Уникальный идентификатор записи. Ключевое поле.
AOGUID="026f0d19-ffcf-448e-bc5c-06d31f911eea" -  Глобальный уникальный идентификатор адресного объекта
PARENTGUID="4660c67b-388d-41f9-a440-79f58de4d73d" -  Идентификатор объекта родительского объекта
PREVID="40911669-e66c-411e-b356-e872fed61b85"  - Идентификатор записи связывания с предыдушей исторической записью
NEXTID="aacfe460-ffb4-4556-9bc7-4f42aa96e1ab"  - Идентификатор записи  связывания с последующей исторической записью
FORMALNAME="Береговая" - Формализованное наименование
OFFNAME="Береговая"  - Официальное наименование
SHORTNAME="ул" -  Краткое наименование типа объекта
AOLEVEL="7" -  Уровень адресного объекта
REGIONCODE="70" - Код региона
AREACODE="003" - Код района
AUTOCODE="0" - Код автономии
CITYCODE="000"  - Код города
CTARCODE="000" -  Код внутригородского района
PLACECODE="010"  - Код населенного пункта
PLANCODE="0000"  - Код элемента планировочной структуры
STREETCODE="0002"  - Код улицы
EXTRCODE="0000"  - Код дополнительного адресообразующего элемента
SEXTCODE="000" -  Код подчиненного дополнительного адресообразующего элемента
PLAINCODE="700030000100002"  - Код адресного объекта из КЛАДР 4.0 одной строкой без признака актуальности (последних двух цифр)
CODE="70003000010000202" -  Код адресного объекта одной строкой с признаком актуальности из КЛАДР 4.0. 
CURRSTATUS="2"  - Статус актуальности КЛАДР 4 (последние две цифры в коде)
ACTSTATUS="0"  - Статус актуальности адресного объекта ФИАС. Актуальный адрес на текущую дату. Обычно последняя запись об адресном объекте.
LIVESTATUS="0" -  Признак действующего адресного объекта
CENTSTATUS="0"  - Статус центра
OPERSTATUS="21"  - Статус действия над записью – причина появления записи (см. описание таблицы OperationStatus):
01 – Инициация;
10 – Добавление;
20 – Изменение;
21 – Групповое изменение;
30 – Удаление;
31 - Удаление вследствие удаления вышестоящего объекта;
40 – Присоединение адресного объекта (слияние);
41 – Переподчинение вследствие слияния вышестоящего объекта;
42 - Прекращение существования вследствие присоединения к другому адресному объекту;
43 - Создание нового адресного объекта в результате слияния адресных объектов;
50 – Переподчинение;
51 – Переподчинение вследствие переподчинения вышестоящего объекта;
60 – Прекращение существования вследствие дробления;
61 – Создание нового адресного объекта в результате дробления

IFNSFL="7025"  - Код ИФНС ФЛ
IFNSUL="7025"  - Код ИФНС ЮЛ
TERRIFNSFL="7002" -  Код территориального участка ИФНС ФЛ
TERRIFNSUL="7002" -  Код территориального участка ИФНС ЮЛ
OKATO="69208810006"  - OKATO
OKTMO="69608410111"  - OKTMO
POSTALCODE="636843"  - Почтовый индекс
STARTDATE="2014-01-10" -  Начало действия записи
ENDDATE="2017-03-01"  - Окончание действия записи
UPDATEDATE="2020-11-29"  - Дата  внесения записи
DIVTYPE="0" - Тип адресации:
                  0 - не определено
                  1 - муниципальный;
                  2 - административно-территориальный
NORMDOC  - Внешний ключ на нормативный документ

'''