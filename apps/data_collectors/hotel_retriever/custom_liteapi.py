from liteapi import LiteApi
from typing import List, Dict, Any, Optional

class CustomLiteApi(LiteApi):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_rates(
        self,
        hotel_ids: List[str],
        checkin: str,
        checkout: str,
        currency: str,
        guest_nationality: str,
        occupancies: List[Dict[str, Any]],
        timeout: int = 6,
        room_mapping: bool = True
    ) -> Dict[str, Any]:
        if not hotel_ids:
            return {"status": "failed", "errors": ["Hotel IDs are required"]}
        if not checkin or not checkout:
            return {"status": "failed", "errors": ["Check-in and check-out dates are required"]}
        if not occupancies:
            return {"status": "failed", "errors": ["Occupancies are required"]}

        payload = {
            "hotelIds": hotel_ids,
            "occupancies": occupancies,
            "currency": currency,
            "guestNationality": guest_nationality,
            "checkin": checkin,
            "checkout": checkout,
            "timeout": timeout,
            "roomMapping": room_mapping
        }

        url = f"{self.service_url}/hotels/rates"

        return self._make_request(url, method='POST', data=payload)