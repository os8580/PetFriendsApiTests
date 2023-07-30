import pytest

from api import PetFriens
from settings import valid_email, valid_password
import os

pf = PetFriens()


# Ниже 5 позитивных тестов
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Дефолтный кот', animal_type='уличный',
                                     age='4', pet_photo='images/cat_stepan.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


# Ниже 10 негативных тестов
def test_get_api_key_for_invalid_user():
    """Test that requesting API key with invalid email and password returns status code 401"""
    invalid_email = 'invalid@example.com'
    invalid_password = 'invalid_password'
    status, result = pf.get_api_key(invalid_email, invalid_password)
    assert status == 403  # The provided combination of user email and password is incorrect


def test_get_all_pets_with_invalid_key():
    """Test that an invalid API key cannot retrieve the list of pets"""
    status, result = pf.get_list_of_pets({'key': 'invalid_key'}, filter='')
    assert status == 403  # The provided auth_key is incorrect
    assert 'pets' not in result


def test_get_all_pets_without_api_key():
    """Test getting a list of pets without providing an API key"""
    with pytest.raises(KeyError):
        pf.get_list_of_pets({}, '')


def test_update_pet_info_without_authentication():
    """Test updating pet information without providing authentication"""
    pet_id = 'valid_pet_id'
    with pytest.raises(KeyError):
        pf.update_pet_info({}, pet_id, 'New Name', 'New Type', 5)


def test_delete_pet_without_authentication():
    """Test deleting a pet without providing authentication"""
    pet_id = 'valid_pet_id'
    with pytest.raises(KeyError):
        pf.delete_pet({}, pet_id)


def test_add_new_pet_with_invalid_image():
    """Test adding a new pet with an invalid image file"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    invalid_image = 'invalid_image.jpg'  # Non-existent image file
    with pytest.raises(FileNotFoundError):
        status, result = pf.add_new_pet(auth_key, 'Invalid Pet', 'Dog', '2', invalid_image)


def test_get_all_pets_with_invalid_filter():
    """Test getting a list of pets with an invalid filter"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    invalid_filter = 'invalid_filter'
    status, result = pf.get_list_of_pets(auth_key, invalid_filter)
    assert status == 500
    assert 'Filter value is incorrect' in result  # Error detail should be provided


def test_update_pet_info_with_invalid_id(name='New Name', animal_type='New Type', age=3):
    """Test updating pet information with an invalid pet ID"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    invalid_pet_id = 'invalid_id'
    status, result = pf.update_pet_info(auth_key, invalid_pet_id, name, animal_type, age)
    assert status == 400  # Not Found


def test_add_new_pet_with_invalid_data():
    """Test adding a pet with missing or invalid data"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    invalid_image = 'invalid_image.jpg'  # Non-existent image file
    with pytest.raises(FileNotFoundError):
        pf.add_new_pet(auth_key, 'Invalid Pet', 'Dog', '2', invalid_image)
    assert not os.path.exists(invalid_image)  # Verify that the invalid image file does not exist


def test_add_new_pet_with_missing_data():
    """Test adding a new pet with missing required data"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    with pytest.raises(FileNotFoundError):
        pf.add_new_pet(auth_key, '', 'Cat', '3', 'images/cat.jpg')
