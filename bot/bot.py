import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.enums import ParseMode
from config import BOT_TOKEN, DB_PATH
from database import Database

BUDGET_RANGES = {
    "budget": "💰 ДО 1.5 МЛН",
    "medium": "💵 1.5-2.5 МЛН",
    "premium": "💎 ОТ 2.5 МЛН"
}

CAR_CATEGORIES = {
    "taxi": "🚕 ТАКСИ",
    "courier": "🚚 КУРЬЕР"
}

BUDGET_BUTTONS = {
    "budget": "💰 ДО 1.5 МЛН",
    "medium": "💵 1.5-2.5 МЛН",
    "premium": "💎 ОТ 2.5 МЛН"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()
user_states = {}


class FuelAPI:
    async def get_fuel_price(self):
        return 55.20

    async def calculate_cost_per_km(self, fuel_consumption_l_per_100km):
        fuel_price = await self.get_fuel_price()
        liters_per_km = fuel_consumption_l_per_100km / 100
        return round(liters_per_km * fuel_price, 2)


fuel_api = FuelAPI()


def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CAR_CATEGORIES["taxi"])],
            [KeyboardButton(text=CAR_CATEGORIES["courier"])],
            [KeyboardButton(text="⭐ МОЁ ИЗБРАННОЕ")],
            [KeyboardButton(text="ℹ️ О БОТЕ")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_budget_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUDGET_BUTTONS["budget"])],
            [KeyboardButton(text=BUDGET_BUTTONS["medium"])],
            [KeyboardButton(text=BUDGET_BUTTONS["premium"])],
            [KeyboardButton(text="↪️ НАЗАД")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_cars_inline_keyboard(cars, show_favorites=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for car in cars:
        button_text = f"{car['name']} - {car['price']:,} ₽"
        if show_favorites:
            button = InlineKeyboardButton(
                text=button_text,
                callback_data=f"view_fav_{car['id']}"
            )
        else:
            button = InlineKeyboardButton(
                text=button_text,
                callback_data=f"car_{car['id']}"
            )
        keyboard.inline_keyboard.append([button])
    if not show_favorites:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="↪️ НАЗАД К ВЫБОРУ БЮДЖЕТА",
                callback_data="back_to_budget"
            )
        ])
    return keyboard


def get_car_detail_keyboard(car_id, user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    is_favorite = db.is_in_favorites(user_id, car_id)
    if is_favorite:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="❌ УДАЛИТЬ ИЗ ИЗБРАННОГО",
                callback_data=f"remove_fav_{car_id}"
            )
        ])
    else:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="⭐ ДОБАВИТЬ В ИЗБРАННОЕ",
                callback_data=f"add_fav_{car_id}"
            )
        ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="⚖️ СРАВНИТЬ",
            callback_data=f"compare_{car_id}"
        )
    ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="↪️ НАЗАД К СПИСКУ",
            callback_data="back_to_cars_list"
        )
    ])
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    db.save_user(user.id, user.username)
    welcome_text = """
🚗 *Добро пожаловать в АвтоЭксперт!*
Я помогу вам выбрать оптимальные автомобили для бизнеса:
• 🚕 **Такси-сервисы** - пассажирские перевозки
• 🚚 **Курьерские службы** - доставка грузов
*Новые возможности:*
⭐ *Избранное* - сохраняйте понравившиеся автомобили
*Как это работает:*
1️⃣ Выберите тип перевозок
2️⃣ Укажите бюджет на 1 автомобиль  
3️⃣ Получите персонализированные рекомендации
4️⃣ Сохраняйте понравившиеся авто в избранное
*Начнем? Выберите тип перевозок ниже* 👇
    """
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())


@dp.message(lambda m: m.text == "⭐ МОЁ ИЗБРАННОЕ")
async def handle_favorites(message: Message):
    user_id = message.from_user.id
    favorites = db.get_user_favorites(user_id)
    if not favorites:
        await message.answer(
            "⭐ *Ваше избранное пусто*\n\n"
            "Чтобы добавить автомобиль в избранное:\n"
            "1. Выберите тип перевозок\n"
            "2. Выберите бюджет\n"
            "3. Нажмите на автомобиль\n"
            "4. Нажмите кнопку '⭐ ДОБАВИТЬ В ИЗБРАННОЕ'\n\n"
            "Избранные автомобили будут сохраняться здесь!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_keyboard()
        )
        return
    response_text = "⭐ *ВАШЕ ИЗБРАННОЕ*\n\n"
    for i, car in enumerate(favorites, 1):
        category = "🚕 Такси" if car["category"] == "taxi" else "🚚 Курьер"
        response_text += f"{i}. *{car['name']}*\n"
        response_text += f"   💰 {car['price']:,} ₽ | {category}\n"
    response_text += "\n👇 *Выберите автомобиль для подробной информации:*"
    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN,
                         reply_markup=get_cars_inline_keyboard(favorites, show_favorites=True))


@dp.message(lambda m: m.text == CAR_CATEGORIES["taxi"])
async def handle_taxi(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {"category": "taxi"}
    await message.answer(
        f"{CAR_CATEGORIES['taxi']} *Отлично! Вы выбрали ТАКСИ*\n\n"
        "Теперь выберите бюджет на 1 автомобиль:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_budget_keyboard()
    )


@dp.message(lambda m: m.text == CAR_CATEGORIES["courier"])
async def handle_courier(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {"category": "courier"}
    await message.answer(
        f"{CAR_CATEGORIES['courier']} *Отлично! Вы выбрали КУРЬЕРСКУЮ СЛУЖБУ*\n\n"
        "Теперь выберите бюджет на 1 автомобиль:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_budget_keyboard()
    )


@dp.message(lambda m: m.text in BUDGET_BUTTONS.values())
async def handle_budget(message: Message):
    user_id = message.from_user.id
    budget_text = message.text
    budget_key = None
    for key, value in BUDGET_BUTTONS.items():
        if value == budget_text:
            budget_key = key
            break
    if not budget_key:
        await message.answer("Ошибка выбора бюджета")
        return
    user_state = user_states.get(user_id, {})
    category = user_state.get("category", "taxi")
    db.save_query(user_id, category, budget_key)
    cars = db.get_cars_by_filters(category, budget_key, limit=5)
    if not cars:
        await message.answer(
            "😕 *К сожалению, нет автомобилей по выбранным критериям*\n\n"
            "Попробуйте выбрать другой бюджет.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_keyboard()
        )
        return
    fuel_price = await fuel_api.get_fuel_price()
    category_name = CAR_CATEGORIES.get(category, "ТАКСИ")
    response_text = f"""
🏆 *РЕКОМЕНДАЦИИ ДЛЯ {category_name}*
*Бюджет: {budget_text}*
*Текущая цена на бензин АИ-95: {fuel_price} ₽/л*
*Доступные варианты:*
"""
    for i, car in enumerate(cars, 1):
        response_text += f"\n{i}. *{car['name']}* - {car['price']:,} ₽"
    response_text += "\n\n👇 *Выберите автомобиль для подробной информации:*"
    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN,
                         reply_markup=get_cars_inline_keyboard(cars))


@dp.message(lambda m: m.text == "ℹ️ О БОТЕ")
async def handle_about(message: Message):
    about_text = """
🤖 *АвтоЭксперт*
Помогает бизнесу выбрать оптимальные автомобили
*Возможности:*
• Подбор авто для такси и курьерских служб
• Фильтрация по бюджету
• Учет текущих цен на топливо
• Детальные характеристики автомобилей
• *Избранное* - сохраняйте понравившиеся авто
• *Сравнение* - вы можете сравнить два автомобиля, для этого нажмите сравнить в карточке одного автомобиля и в карточке другого автомобиля
Просто выбирайте тип перевозок и бюджет!
    """
    await message.answer(about_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())


@dp.message(lambda m: m.text == "↪️ НАЗАД")
async def handle_back(message: Message):
    await message.answer("Выберите тип перевозок:", reply_markup=get_main_keyboard())


@dp.callback_query(lambda c: c.data.startswith("car_"))
async def handle_car_detail(callback: CallbackQuery):
    try:
        car_id = int(callback.data.split("_")[1])
        await show_car_detail(callback, car_id)
    except Exception as e:
        logger.error(f"Ошибка при обработке автомобиля: {e}")
        await callback.answer("Произошла ошибка")


@dp.callback_query(lambda c: c.data.startswith("view_fav_"))
async def handle_favorite_car(callback: CallbackQuery):
    try:
        car_id = int(callback.data.split("_")[2])
        await show_car_detail(callback, car_id, from_favorites=True)
    except Exception as e:
        logger.error(f"Ошибка при обработке избранного: {e}")
        await callback.answer("Произошла ошибка")


async def show_car_detail(callback: CallbackQuery, car_id, from_favorites=False):
    car = db.get_car_by_id(car_id)
    if not car:
        await callback.answer("Автомобиль не найден")
        return
    user_id = callback.from_user.id
    user_state = user_states.get(user_id, {})
    db.save_query(user_id, user_state.get("category", "taxi"),
                  user_state.get("budget", "medium"), car_id)
    fuel_consumption = car.get("fuel_consumption")
    if fuel_consumption:
        cost_per_km = await fuel_api.calculate_cost_per_km(fuel_consumption)
    else:
        cost_per_km = 0
    detail_text = f"""
🚗 *{car['name']}*
📅 *Год выпуска:* {car.get('year', 'Нет данных')}
💰 *Стоимость:* {car['price']:,} ₽
"""
    if fuel_consumption:
        detail_text += f"⛽ *Расход топлива:* {fuel_consumption} л/100км\n"
        detail_text += f"💸 *Стоимость 1 км:* ~{cost_per_km} ₽\n"
    if car.get("reliability"):
        detail_text += f"⭐ *Надежность:* {car['reliability']}\n"
    if car.get("comfort"):
        detail_text += f"🛋️ *Комфорт:* {car['comfort']}/5\n"
    if car.get("cargo_volume"):
        detail_text += f"📦 *Грузовой объем:* {car['cargo_volume']} м³\n"
    detail_text += f"\n📝 *Описание:*\n{car['description']}\n"
    detail_text += f"\n🏆 *Преимущества:*\n{car['advantages']}"
    keyboard = get_car_detail_keyboard(car_id, user_id)
    await callback.message.answer(detail_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("add_fav_"))
async def handle_add_favorite(callback: CallbackQuery):
    try:
        car_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        success = db.add_to_favorites(user_id, car_id)
        if success:
            await callback.answer("✅ Добавлено в избранное!")
            keyboard = get_car_detail_keyboard(car_id, user_id)
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await callback.answer("❌ Не удалось добавить в избранное")
    except Exception as e:
        logger.error(f"Ошибка при добавлении в избранное: {e}")
        await callback.answer("Произошла ошибка")


@dp.callback_query(lambda c: c.data.startswith("remove_fav_"))
async def handle_remove_favorite(callback: CallbackQuery):
    try:
        car_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        db.remove_from_favorites(user_id, car_id)
        await callback.answer("❌ Удалено из избранного")
        keyboard = get_car_detail_keyboard(car_id, user_id)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при удалении из избранного: {e}")
        await callback.answer("Произошла ошибка")


@dp.callback_query(lambda c: c.data == "back_to_cars_list")
async def handle_back_to_cars_list(callback: CallbackQuery):
    await callback.message.answer("Выберите тип перевозок:", reply_markup=get_main_keyboard())
    await callback.answer()


@dp.callback_query(lambda c: c.data == "back_to_budget")
async def handle_back_to_budget(callback: CallbackQuery):
    await callback.message.answer("Выберите бюджет:", reply_markup=get_budget_keyboard())
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("compare_"))
async def handle_compare_fixed(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        car_id = int(callback.data.split("_")[1])
        if user_id not in user_states:
            user_states[user_id] = {}
        if 'compare_list' not in user_states[user_id]:
            user_states[user_id]['compare_list'] = []
        compare_list = user_states[user_id]['compare_list']
        if car_id in compare_list:
            await callback.answer(f"✅ Этот авто уже выбран ({len(compare_list)}/2)")
            return
        compare_list.append(car_id)
        user_states[user_id]['compare_list'] = compare_list
        count = len(compare_list)
        if count == 1:
            car = db.get_car_by_id(car_id)
            if car:
                await callback.answer(f"✅ {car['name']} выбран (1/2)\nВыберите второй авто")
            else:
                await callback.answer("✅ Авто выбран (1/2)\nВыберите второй авто")
        elif count == 2:
            car1_id, car2_id = compare_list[0], compare_list[1]
            car1 = db.get_car_by_id(car1_id)
            car2 = db.get_car_by_id(car2_id)
            if car1 and car2:
                category = car1.get('category', 'taxi')
                text = f"""
🔍 *СРАВНЕНИЕ: {car1['name']} vs {car2['name']}*
💰 *ЦЕНА*
• {car1['name']}: {car1['price']:,} ₽
• {car2['name']}: {car2['price']:,} ₽
→ {'💰 ' + car1['name'] if car1['price'] < car2['price'] else '💰 ' + car2['name']} выгоднее
⛽ *РАСХОД ТОПЛИВА*
• {car1['name']}: {car1.get('fuel_consumption', '—')} л/100км
• {car2['name']}: {car2.get('fuel_consumption', '—')} л/100км
→ {'⛽ ' + car1['name'] if car1.get('fuel_consumption', 10) < car2.get('fuel_consumption', 10) else '⛽ ' + car2['name']} экономичнее
⭐ *НАДЕЖНОСТЬ*
• {car1['name']}: {car1.get('reliability', 0)}
• {car2['name']}: {car2.get('reliability', 0)}
→ {'⭐ ' + car1['name'] if car1.get('reliability', 0) > car2.get('reliability', 0) else '⭐ ' + car2['name']} надежнее
"""
                if category == 'courier':
                    cargo1 = car1.get('cargo_volume', 0)
                    cargo2 = car2.get('cargo_volume', 0)
                    text += f"""
📦 *ГРУЗОВОЙ ОБЪЕМ*
• {car1['name']}: {cargo1 if cargo1 else '—'} м³
• {car2['name']}: {cargo2 if cargo2 else '—'} м³
→ {'📦 ' + car1['name'] if cargo1 > cargo2 else '📦 ' + car2['name']} вместительнее
"""
                else:
                    comfort1 = car1.get('comfort', 0)
                    comfort2 = car2.get('comfort', 0)
                    text += f"""
🛋️ *КОМФОРТ*
• {car1['name']}: {comfort1}
• {car2['name']}: {comfort2}
→ {'🛋️ ' + car1['name'] if comfort1 > comfort2 else '🛋️ ' + car2['name']} комфортнее
"""
                user_states[user_id]['compare_list'] = []
                await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
                await callback.answer("✅ Сравнение завершено")
            else:
                await callback.answer("❌ Ошибка загрузки данных авто")
                user_states[user_id]['compare_list'] = []
        elif count > 2:
            user_states[user_id]['compare_list'] = [car_id]
            await callback.answer("🔄 Начинаем заново с этого авто")
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID автомобиля")
    except Exception:
        await callback.answer("❌ Произошла ошибка")


async def main():
    logger.info("🚀 Запуск бота АвтоЭксперт...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())