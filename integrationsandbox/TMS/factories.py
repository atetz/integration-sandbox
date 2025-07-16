import datetime
import random
from enum import Enum
from typing import List

from faker import Faker

from integrationsandbox.tms.models import (
    EquipmentType,
    ModeType,
    PackageType,
    StopType,
    TmsAddress,
    TmsCustomer,
    TmsLineItem,
    TmsLocation,
    TmsShipment,
    TmsStop,
)


def get_random_enum_choice(enum_attribute: Enum) -> Enum:
    return random.choice(list(enum_attribute))


class TmsShipmentFactory:
    address_locales = ("it_IT", "en_GB", "nl_NL", "fr_FR", "de_DE")
    goods_descriptions = (
        "Industrial steel I-beams, 20-foot lengths, galvanized coating",
        "Bulk organic quinoa grain, 50-pound burlap sacks",
        "Commercial grade vinyl flooring rolls, 12-foot width",
        "Automotive brake pads for heavy-duty trucks, boxed sets",
        "Stainless steel restaurant equipment - 6-burner gas ranges",
        "Polyethylene plastic pellets for manufacturing, bulk bags",
        "Decorative landscape boulders, natural granite, assorted sizes",
        "Electronic circuit boards for appliance manufacturing",
        "Wooden shipping pallets, heat-treated, standard 48x40 inch",
        "Liquid fertilizer concentrate in 55-gallon drums",
        "Rolled copper sheets for roofing applications",
        "Pre-fabricated concrete blocks for retaining walls",
        "Industrial washing machines for commercial laundromats",
        "Bulk coffee beans from Central America, vacuum-sealed bags",
        "Aluminum extrusions for window frame manufacturing",
        "Packaged frozen vegetables for restaurant distribution",
        "Medical oxygen tanks, various sizes, safety certified",
        "Ceramic bathroom tiles in decorative patterns",
        "Heavy-duty truck tires, new and retreaded options",
        "Bulk wheat flour for commercial bakeries",
        "Fiberglass insulation rolls for construction projects",
        "Electronic gaming machines for casino installations",
        "Industrial paper rolls for packaging applications",
        "Liquid soap concentrate in plastic containers",
        "Metal roofing panels with weather-resistant coating",
        "Bulk plastic bottles for beverage manufacturing",
        "Commercial air conditioning units for office buildings",
        "Decorative concrete pavers for landscaping projects",
        "Industrial grade cleaning chemicals in drums",
        "Wooden furniture components for assembly facilities",
        "Bulk rice in moisture-proof packaging",
        "Electrical transformers for power distribution",
        "Synthetic rubber sheets for industrial applications",
        "Commercial kitchen exhaust hoods, stainless steel",
        "Bulk cotton fabric rolls for textile manufacturing",
        "Prefabricated metal building components",
        "Industrial pumps for water treatment facilities",
        "Bulk sugar for food processing plants",
        "Fiberglass reinforcement materials for composites",
        "Commercial refrigeration units for grocery stores",
        "Bulk plastic resin for injection molding",
        "Steel rebar for concrete reinforcement projects",
        "Industrial fans for ventilation systems",
        "Bulk oats for livestock feed production",
        "Aluminum siding panels for residential construction",
        "Commercial grade carpet tiles for office spaces",
        "Industrial conveyor belt sections",
        "Bulk vegetable oil for food service industry",
        "Prefabricated shower units for construction",
        "Electronic control panels for manufacturing equipment",
        "Bulk paper towels for institutional use",
        "Industrial generators for backup power systems",
        "Decorative stone veneer for architectural applications",
        "Commercial grade kitchen equipment - walk-in coolers",
        "Bulk plastic wrap for packaging operations",
        "Steel pipe sections for plumbing installations",
        "Industrial compressors for manufacturing facilities",
        "Bulk dried beans for food distribution",
        "Fiberglass panels for building exteriors",
        "Commercial laundry equipment - industrial dryers",
        "Bulk chemical additives for pool maintenance",
        "Prefabricated garage door sections",
        "Industrial lighting fixtures for warehouse spaces",
        "Bulk corn syrup for food manufacturing",
        "Metal shelving units for warehouse storage",
        "Commercial grade floor mats for high-traffic areas",
        "Industrial safety equipment - protective barriers",
        "Bulk plastic containers for food packaging",
        "Steel structural beams for construction projects",
        "Commercial ice machines for restaurant use",
        "Industrial adhesives in bulk containers",
        "Bulk frozen french fries for food service",
        "Prefabricated concrete septic tanks",
        "Electronic testing equipment for laboratories",
        "Bulk toilet paper for institutional facilities",
        "Industrial water heaters for commercial buildings",
        "Decorative architectural panels for facades",
        "Commercial grade exercise equipment",
        "Bulk spices and seasonings for food processing",
        "Steel storage tanks for industrial applications",
        "Industrial vacuum systems for manufacturing",
        "Bulk plastic pellets for 3D printing applications",
        "Prefabricated utility sheds for residential use",
        "Commercial grade security systems and cameras",
        "Industrial paint in 55-gallon drums",
        "Bulk cheese products for food service industry",
        "Metal fence panels and posts for perimeter security",
        "Commercial grade floor polishers and buffers",
        "Industrial hydraulic equipment and components",
        "Bulk breakfast cereals for institutional use",
        "Prefabricated building trusses for construction",
        "Commercial grade restaurant furniture sets",
        "Industrial waste management containers",
        "Bulk powdered milk for food manufacturing",
        "Steel dock levelers for loading facilities",
        "Commercial grade carpet cleaning equipment",
        "Industrial grade fasteners and hardware",
        "Bulk frozen meat products for distribution",
        "Prefabricated modular office components",
        "Commercial grade outdoor playground equipment",
    )

    def get_random_measurement(self):
        return self.fake.pyfloat(
            positive=True, min_value=15, max_value=200, right_digits=2
        )

    def get_random_weight(self):
        return self.fake.pyfloat(
            positive=True, min_value=150, max_value=12000, right_digits=2
        )

    def get_random_goods_description(self):
        return random.choice(self.goods_descriptions)

    def get_random_days_to_stop(self):
        days_to_stop = 7
        return datetime.timedelta(days=random.randint(1, days_to_stop))

    def __init__(self):
        self.fake = Faker()

    def create_customer(self) -> TmsCustomer:
        return TmsCustomer(
            id=self.fake.uuid4(),
            name=self.fake.company(),
            carrier=f"{self.fake.company()} Transport",
        )

    def create_line_item(self) -> TmsLineItem:
        return TmsLineItem(
            package_type=get_random_enum_choice(PackageType),
            stackable=self.fake.boolean(),
            height=self.get_random_measurement(),
            length=self.get_random_measurement(),
            width=self.get_random_measurement(),
            length_unit="CM",
            package_weight=self.get_random_weight(),
            weight_unit="KG",
            description=self.get_random_goods_description(),
            total_packages=self.fake.random_int(min=1, max=50),
        )

    def create_address(self, localed_faker: Faker) -> TmsAddress:
        return TmsAddress(
            address=localed_faker.street_address(),
            city=localed_faker.city(),
            postal_code=localed_faker.postcode(),
            country=localed_faker.current_country_code(),
        )

    def create_location(self) -> TmsLocation:
        localed_faker = Faker(random.choice(self.address_locales))
        return TmsLocation(
            code=self.fake.bothify(text="LOC-####"),
            name=localed_faker.company(),
            address=self.create_address(localed_faker),
            latitude=localed_faker.latitude(),
            longitude=localed_faker.longitude(),
        )

    def create_stops(self) -> List[TmsStop]:
        today = datetime.date.today()
        pickup_date = today + self.get_random_days_to_stop()
        delivery_date = pickup_date + self.get_random_days_to_stop()

        pickup = TmsStop(
            type=StopType.PICKUP,
            location=self.create_location(),
            planned_date=pickup_date,
            planned_time_window_start=datetime.time(6, 0, 0),
            planned_time_window_end=datetime.time(17, 0, 0),
        )

        delivery = TmsStop(
            type=StopType.DELIVERY,
            location=self.create_location(),
            planned_date=delivery_date,
            planned_time_window_start=datetime.time(6, 0, 0),
            planned_time_window_end=datetime.time(17, 0, 0),
        )

        return [pickup, delivery]

    def create_shipment(self) -> TmsShipment:
        return TmsShipment(
            id=self.fake.unique.uuid4(),
            external_reference=None,
            mode=get_random_enum_choice(ModeType),
            equipment_type=get_random_enum_choice(EquipmentType),
            customer=self.create_customer(),
            line_items=[self.create_line_item() for i in range(random.randint(1, 20))],
            stops=self.create_stops(),
            timeline_events=None,
        )
