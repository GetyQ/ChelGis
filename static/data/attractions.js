// Данные о достопримечательностях для демонстрации
// Этот файл используется только для справки и подготовки данных
// Основные данные берутся из базы данных через API

const ATTRACTIONS_DATA = [
    {
        id: 1,
        name: "Государственный исторический музей Южного Урала",
        description: "Один из крупнейших музеев Урала с богатой коллекцией исторических артефактов.",
        lat: 55.159388,
        lng: 61.402429,
        address: "ул. Труда, 100",
        category: "Музей",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 2,
        name: "Театр оперы и балета им. М.И. Глинки",
        description: "Знаменитый оперный театр, одна из архитектурных жемчужин Челябинска.",
        lat: 55.159806,
        lng: 61.394305,
        address: "пл. Ярославского, 1",
        category: "Культура",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 3,
        name: "Парк им. Ю.А. Гагарина",
        description: "Крупнейший парк города с аттракционами, зоопарком и местами для отдыха.",
        lat: 55.164165,
        lng: 61.372882,
        address: "ул. Коммуны, 98",
        category: "Парк",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 4,
        name: "Челябинский областной краеведческий музей",
        description: "Музей, посвященный природе и истории Челябинской области.",
        lat: 55.158631,
        lng: 61.402026,
        address: "ул. Труда, 100",
        category: "Музей",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 5,
        name: "Площадь Революции",
        description: "Центральная площадь Челябинска с памятником В.И. Ленину.",
        lat: 55.160300,
        lng: 61.403119,
        address: "Площадь Революции",
        category: "Площадь",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 6,
        name: "Сквер им. А.С. Пушкина",
        description: "Уютный сквер в центре города с фонтаном и памятником Пушкину.",
        lat: 55.155966,
        lng: 61.392933,
        address: "ул. Пушкина",
        category: "Парк",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 7,
        name: "Челябинский зоопарк",
        description: "Зоопарк с разнообразной коллекцией животных со всего мира.",
        lat: 55.163543,
        lng: 61.367906,
        address: "ул. Труда, 191",
        category: "Зоопарк",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 8,
        name: "Церковь Александра Невского",
        description: "Красивый православный храм, построенный в конце XIX века.",
        lat: 55.151906,
        lng: 61.379844,
        address: "ул. Цвиллинга, 62",
        category: "Религия",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 9,
        name: "Железнодорожный вокзал Челябинска",
        description: "Историческое здание вокзала, архитектурный памятник города.",
        lat: 55.150811,
        lng: 61.414520,
        address: "Привокзальная площадь, 1",
        category: "Архитектура",
        image_url: "https://via.placeholder.com/150"
    },
    {
        id: 10,
        name: "Центральный стадион",
        description: "Главная спортивная арена города Челябинска.",
        lat: 55.163173,
        lng: 61.390619,
        address: "ул. Коммуны, 98",
        category: "Спорт",
        image_url: "https://via.placeholder.com/150"
    }
];
