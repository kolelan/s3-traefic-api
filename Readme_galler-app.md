# React приложение для просмотра загруженных файлов

1. Создать React-приложение
```bash
npx create-react-app gallery-app
cd gallery-app
```

2. Установить зависимости
```bash
npm install glightbox
```
3. Подготовить структуру проекта

```txt
gallery-app/
├── public/
│   ├── report.json  # поместите ваш файл сюда
│   └── index.html
├── src/
│   ├── components/
│   │   └── Gallery.js  # наш компонент
│   ├── App.js
│   ├── index.js
│   └── styles.css     # стили из примера
└── package.json
```

4. Создать компонент Gallery