MATERIAL_CHOICES = (
    ("stainless_steel", "Нержавеющая сталь"),
    ("enameled_steel", "Эмалированная сталь"),
    ("ceramic_pipe", "Керамическая труба"),
    ("galvanized_steel", "Оцинкованная сталь"),
    ("structural_steel", "Конструкционная сталь"),
    ("boiler_steel", "Котловая сталь"),
    ("cast_iron", "Чугун"),
    ("ceramics", "Керамика"),
    ("natural_stone", "Натуральный камень"),
    ("iron", "Железо"),
    ("fireclay", "Шамот"),
    ("talc_magnesium", "Талькомагнезит"),
    ("metal", "Металл"),
)

FIREBOX_MATERIAL_CHOICES = (
    ("steel", "Стальной"),
    ("fireclay", "Шамотный"),
    ("cast_iron", "Чугунный"),
    ("cellular_cast_iron", "Цельнолитый чугунный"),
)

STONE_MATERIAL_CHOICES = (
    ("natural", "Натуральный"),
    ("artificial", "Искусственный"),
)

DOOR_TYPE_CHOICES = (
    ("with_glass", "Со стеклом"),
    ("without_glass", "Без стекла"),
)

DOOR_MECHANISM_CHOICES = (
    ("side_opening", "Боковое открывание"),
    ("lift_up", "Подъемный механизм"),
)

FIRE_VIEW_CHOICES = (
    ("straight_glass", "Прямое стекло"),
    ("panoramic_glass", "Панорамное стекло"),
    ("g_shaped_glass", "Г-образное стекло"),
    ("p_shaped_glass", "П-образное стекло"),
    ("prismatic_glass", "Призматическое стекло"),
    ("lift_up_mechanism", "Подъемный механизм"),
    ("double_sided", "Двухстороннее"),
)

GLASS_COUNT_CHOICES = (
    ("one", "Одно"),
    ("two", "Два"),
    ("three", "Три"),
    ("four", "Четыре"),
)

FUEL_TYPE_CHOICES = (
    ("gas", "Газ"),
    ("wood", "Дровяной"),
    ("electric", "Электрический"),
    ("coal", "Угольный"),
    ("solid_fuel", "Твердотопливный"),
    ("semi_automatic", "Полуавтоматический"),
    ("bioethanol", "Биоэтанол"),
    ("pellet", "Пеллетный"),
)

TANK_TYPE_CHOICES = (
    ("samovar", "Самоварный"),
    ("mounted", "Навесной"),
    ("register", "Регистр"),
)

FIREBOX_TYPE_CHOICES = (
    ("with_extension", "С выносом"),
    ("without_extension", "Без выноса"),
)

STONE_TYPE_CHOICES = (
    ("closed", "Закрытая"),
    ("open", "Открытая"),
    ("combined", "Комбинированная"),
    ("stone_mesh", "Сетка для камней"),
)

WATER_HEATING_CHOICES = (
    ("with_heat_exchanger", "С теплообменником"),
    ("without_heat_exchanger", "Без теплообменника"),
)

PLACEMENT_CHOICES = (
    ("horizontal", "Горизонтальная"),
    ("vertical", "Вертикальная"),
    ("corner", "Угловая"),
    ("central", "Центральная"),
)

FACING_TYPE_CHOICES = (
    ("built_in", "Встроенный"),
    ("double_sided", "Двусторонний"),
    ("fireplace_frame", "Каминная рамка"),
    ("wall_mounted", "Пристенный"),
    ("corner", "Угловой"),
    ("central", "Центральный"),
)
