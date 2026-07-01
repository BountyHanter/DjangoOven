from main_app.models import (
    Product,
    ProductAttribute,
    ProductAttributeOption,
    ProductAttributeValue,
    ProductImage,
    ProductVideo,
    Section,
)
from main_app.models.manufacturer import Manufacturer


def _add_choice(product, attribute, option):
    return ProductAttributeValue.objects.create(
        product=product,
        attribute=attribute,
        option=option,
    )


def _add_number(product, attribute, value):
    return ProductAttributeValue.objects.create(
        product=product,
        attribute=attribute,
        value_number=value,
    )


def _add_bool(product, attribute, value):
    return ProductAttributeValue.objects.create(
        product=product,
        attribute=attribute,
        value_bool=value,
    )


def create_catalog_filter_dataset():
    aurora = Manufacturer.objects.create(
        name="Aurora",
        slug="aurora",
        logo="manufacturers/aurora.webp",
        is_active=True,
        priority=100,
    )
    bathlab = Manufacturer.objects.create(
        name="BathLab",
        slug="bathlab",
        logo="manufacturers/bathlab.webp",
        is_active=True,
        priority=50,
    )

    root = Section.objects.create(
        name="Каталог",
        slug="catalog-root",
        ordering=1,
        image="sections/catalog-root.webp",
        description_main="Главный раздел каталога",
        browser_title="Каталог печей",
        description="Полное описание каталога",
        meta_description="SEO описание каталога",
        meta_keywords="каталог, печи",
    )
    stoves = Section.objects.create(
        name="Печи",
        slug="stoves",
        parent=root,
        ordering=1,
        image="sections/stoves.webp",
        description_main="Раздел с печами",
        browser_title="Печи",
        description="Полное описание раздела печей",
        meta_description="SEO описание печей",
        meta_keywords="печи",
    )
    wood = Section.objects.create(
        name="Дровяные печи",
        slug="wood-fired-stoves",
        parent=stoves,
        ordering=1,
        image="sections/wood-fired-stoves.webp",
    )
    electric = Section.objects.create(
        name="Электрические печи",
        slug="electric-stoves",
        parent=stoves,
        ordering=2,
        image="sections/electric-stoves.webp",
    )
    gas = Section.objects.create(
        name="Газовые печи",
        slug="gas-stoves",
        parent=stoves,
        ordering=3,
        image="sections/gas-stoves.webp",
    )
    accessories = Section.objects.create(
        name="Комплекты",
        slug="accessories",
        parent=root,
        ordering=2,
        image="sections/accessories.webp",
    )

    fuel = ProductAttribute.objects.create(
        name="Тип топлива",
        slug="fuel-type",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    finish = ProductAttribute.objects.create(
        name="Материал отделки",
        slug="finish-material",
        type=ProductAttribute.AttributeType.CHOICE,
        allow_multiple=True,
    )
    power = ProductAttribute.objects.create(
        name="Мощность",
        slug="moshchnost",
        type=ProductAttribute.AttributeType.NUMBER,
        unit="кВт",
    )
    steam_volume = ProductAttribute.objects.create(
        name="Объем парной",
        slug="steam-volume",
        type=ProductAttribute.AttributeType.NUMBER,
        unit="м3",
    )
    water_circuit = ProductAttribute.objects.create(
        name="Водяной контур",
        slug="water-circuit",
        type=ProductAttribute.AttributeType.BOOLEAN,
    )
    glass_lift = ProductAttribute.objects.create(
        name="Подъемное стекло",
        slug="glass-lift",
        type=ProductAttribute.AttributeType.BOOLEAN,
    )
    long_fire = ProductAttribute.objects.create(
        name="Длинная топка",
        slug="long-fire",
        type=ProductAttribute.AttributeType.BOOLEAN,
        hide_in_filter=True,
    )

    wood_fuel = ProductAttributeOption.objects.create(
        attribute=fuel,
        value="Дрова",
        slug="wood",
    )
    electric_fuel = ProductAttributeOption.objects.create(
        attribute=fuel,
        value="Электричество",
        slug="electric",
    )
    gas_fuel = ProductAttributeOption.objects.create(
        attribute=fuel,
        value="Газ",
        slug="gas",
    )

    steel = ProductAttributeOption.objects.create(
        attribute=finish,
        value="Сталь",
        slug="steel",
    )
    soapstone = ProductAttributeOption.objects.create(
        attribute=finish,
        value="Талькохлорит",
        slug="soapstone",
    )
    ceramic = ProductAttributeOption.objects.create(
        attribute=finish,
        value="Керамика",
        slug="ceramic",
    )
    cast_iron = ProductAttributeOption.objects.create(
        attribute=finish,
        value="Чугун",
        slug="cast-iron",
    )

    aurora_pro = Product.objects.create(
        name="Aurora Pro 18 Duo",
        manufacturer=aurora,
        price=162000,
        discount_price=129000,
        is_active=True,
        is_new=True,
        is_bestseller=True,
        priority=1,
        sku="AUR-PRO-18, AUR-PRO-18-DUO",
        series="Aurora Pro",
        description="Дровяная печь с большой каменкой и выносной топкой.",
    )
    aurora_pro.sections.add(wood, accessories)
    ProductImage.objects.create(
        product=aurora_pro,
        image="products/images/aurora-pro-side.webp",
        ordering=10,
    )
    ProductImage.objects.create(
        product=aurora_pro,
        image="products/images/aurora-pro-main.webp",
        is_main=True,
        ordering=20,
    )
    ProductVideo.objects.create(
        product=aurora_pro,
        url="https://video.example.com/aurora-pro-review.mp4",
        preview_url="https://cdn.example.com/aurora-pro-preview.webp",
        ordering=1,
    )
    _add_choice(aurora_pro, fuel, wood_fuel)
    _add_choice(aurora_pro, finish, steel)
    _add_choice(aurora_pro, finish, soapstone)
    _add_number(aurora_pro, power, "18.50")
    _add_number(aurora_pro, steam_volume, "24.00")
    _add_bool(aurora_pro, water_circuit, True)
    _add_bool(aurora_pro, glass_lift, False)
    _add_bool(aurora_pro, long_fire, True)

    aurora_compact = Product.objects.create(
        name="Aurora Compact 14",
        manufacturer=aurora,
        price=99000,
        is_active=True,
        is_bestseller=False,
        priority=3,
        sku="AUR-COMPACT-14",
        series="Aurora Compact",
        description="Компактная дровяная печь для небольшой парной.",
    )
    aurora_compact.sections.add(wood)
    ProductImage.objects.create(
        product=aurora_compact,
        image="products/images/aurora-compact-main.webp",
        is_main=True,
        ordering=1,
    )
    _add_choice(aurora_compact, fuel, wood_fuel)
    _add_choice(aurora_compact, finish, steel)
    _add_number(aurora_compact, power, "14.00")
    _add_number(aurora_compact, steam_volume, "18.00")
    _add_bool(aurora_compact, water_circuit, True)
    _add_bool(aurora_compact, glass_lift, False)
    _add_bool(aurora_compact, long_fire, False)

    bathlab_electric = Product.objects.create(
        name="BathLab Electro 10",
        manufacturer=bathlab,
        price=75000,
        discount_price=69000,
        is_active=True,
        is_new=True,
        sku="BL-ELECTRO-10",
        series="BathLab Electro",
        description="Электрическая печь с керамической облицовкой.",
    )
    bathlab_electric.sections.add(electric)
    ProductImage.objects.create(
        product=bathlab_electric,
        image="products/images/bathlab-electro-main.webp",
        is_main=True,
        ordering=1,
    )
    _add_choice(bathlab_electric, fuel, electric_fuel)
    _add_choice(bathlab_electric, finish, ceramic)
    _add_number(bathlab_electric, power, "10.00")
    _add_number(bathlab_electric, steam_volume, "12.00")
    _add_bool(bathlab_electric, water_circuit, False)
    _add_bool(bathlab_electric, glass_lift, True)
    _add_bool(bathlab_electric, long_fire, False)

    bathlab_gas = Product.objects.create(
        name="BathLab Gas 22",
        manufacturer=bathlab,
        price=210000,
        is_active=True,
        is_bestseller=True,
        priority=2,
        sku="BL-GAS-22",
        series="BathLab Gas",
        description="Газовая печь с чугунной топкой.",
    )
    bathlab_gas.sections.add(gas)
    ProductImage.objects.create(
        product=bathlab_gas,
        image="products/images/bathlab-gas-main.webp",
        is_main=True,
        ordering=1,
    )
    ProductVideo.objects.create(
        product=bathlab_gas,
        url="https://video.example.com/bathlab-gas-installation.mp4",
        preview_url="https://cdn.example.com/bathlab-gas-preview.webp",
        ordering=1,
    )
    _add_choice(bathlab_gas, fuel, gas_fuel)
    _add_choice(bathlab_gas, finish, cast_iron)
    _add_number(bathlab_gas, power, "22.00")
    _add_number(bathlab_gas, steam_volume, "30.00")
    _add_bool(bathlab_gas, water_circuit, False)
    _add_bool(bathlab_gas, glass_lift, True)
    _add_bool(bathlab_gas, long_fire, True)

    aurora_accessory = Product.objects.create(
        name="Aurora Installation Kit",
        manufacturer=aurora,
        price=45000,
        is_active=True,
        sku="AUR-KIT",
        series="Aurora Accessories",
        description="Комплект дымохода и монтажных элементов.",
    )
    aurora_accessory.sections.add(accessories)
    ProductImage.objects.create(
        product=aurora_accessory,
        image="products/images/aurora-kit-main.webp",
        is_main=True,
        ordering=1,
    )

    inactive = Product.objects.create(
        name="Aurora Hidden Prototype",
        manufacturer=aurora,
        price=50000,
        is_active=False,
        sku="AUR-HIDDEN",
    )
    inactive.sections.add(wood)
    _add_choice(inactive, fuel, wood_fuel)
    _add_number(inactive, power, "9.00")

    return {
        "manufacturers": {
            "aurora": aurora,
            "bathlab": bathlab,
        },
        "sections": {
            "root": root,
            "stoves": stoves,
            "wood": wood,
            "electric": electric,
            "gas": gas,
            "accessories": accessories,
        },
        "attributes": {
            "fuel": fuel,
            "finish": finish,
            "power": power,
            "steam_volume": steam_volume,
            "water_circuit": water_circuit,
            "glass_lift": glass_lift,
            "long_fire": long_fire,
        },
        "options": {
            "wood_fuel": wood_fuel,
            "electric_fuel": electric_fuel,
            "gas_fuel": gas_fuel,
            "steel": steel,
            "soapstone": soapstone,
            "ceramic": ceramic,
            "cast_iron": cast_iron,
        },
        "products": {
            "aurora_pro": aurora_pro,
            "aurora_compact": aurora_compact,
            "bathlab_electric": bathlab_electric,
            "bathlab_gas": bathlab_gas,
            "aurora_accessory": aurora_accessory,
            "inactive": inactive,
        },
    }
