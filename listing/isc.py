import json
from requests import Session


class ISC:
    name: str = "Independent Schools Council"
    base_url: str = "https://www.isc.co.uk"
    api_schools_count: str = f"{base_url}/umbraco/api/ISCSchools/GetSchoolCount/"
    api_schools_list: str = f"{base_url}/Umbraco/Api/FindSchoolApi/FindSchoolListResults"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"

    def __init__(self, take: int = 100):
        self.session: Session = Session()
        self.skip: int = 0
        self.take: int = take
        self.headers: dict = self.get_headers()

    def get_headers(self):
        return {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'{self.base_url}/',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': self.base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

    def get_payload(self):
        return {
            "locationLatitude": None,
            "locationLongitude": None,
            "distanceInMiles": 0,
            "residencyTypes": [],
            "genderGroup": None,
            "ageRange": None,
            "religiousAffiliation": None,
            "financialAssistances": [],
            "examinations": [],
            "specialNeeds": False,
            "scholarshipsAndBurseries": False,
            "latitudeSW": 47.823214345168694,
            "longitudeSW": -21.20264015625,
            "latitudeNE": 59.385618287793505,
            "longitudeNE": 16.10693015625002,
            "contactCountyID": 0,
            "contactCountryID": 0,
            "londonBoroughID": 0,
            "filterByBounds": True,
            "savedBounds": True,
            "zoom": 5,
            "center": {
                "lat": 54.00366,
                "lng": -2.547855
            }
        }

    def get_school_count(self) -> [int, None]:
        response = self.session.get(url=self.api_schools_count, headers=self.headers)
        if response.ok:
            return int(response.text)
        else:
            return None

    def get_schools(self) -> [list, None]:
        response = self.session.post(
            url=self.api_schools_list,
            headers=self.headers,
            params={"skip": self.skip, "take": self.take},
            data=json.dumps(self.get_payload())
        )
        if response.ok:
            return json.loads(response.text)
        else:
            return None

    def get_all_schools(self):
        school_count = self.get_school_count()
        if school_count is None:
            return None

        school_list = []

        while len(school_list) != school_count:
            response = self.get_schools()
            if response is None:
                print(f"failed to get schools for params: skip={self.skip} and take={self.take}")
                return school_list

            school_list.extend(response)
            print(f"{len(school_list)} / {school_count}")

            if self.skip < school_count and (self.skip + self.take) < school_count:
                self.skip = self.skip + self.take
            else:
                self.skip = self.skip + (school_count - self.skip)

        return school_list


isc = ISC()
schools = isc.get_all_schools()
