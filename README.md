## Hello World 😎

```java
public class DeveloperProfile {

    public static void main(String[] args) {
        Developer artem = new Developer();
        artem.name       = "Artem";
        artem.role       = "🧠 Beginner Architect";
        artem.experience = "💼 10+ years";
        artem.location   = "🌍 Russia";
        artem.languages  = new String[]{"Java", "Python", "JavaScript", "PHP", "Lua"};
        artem.email      = "📬 archibk32@yandex.ru";
        artem.telegram   = "@tirexswa";

        artem.introduce();
    }
}

class Developer {
    String name;
    String role;
    String experience;
    String location;
    String[] languages;
    String email;
    String telegram;

    void introduce() {
        System.out.println("👋 Hi, I'm " + name);
        System.out.println(role + " based in " + location);
        System.out.println("Experience: " + experience);
        System.out.print("Tech stack: ");
        for (String lang : languages) System.out.print(lang + " ");
        System.out.println("\nContact: " + email + " | Telegram: " + telegram);
        System.out.println("🛠️ Building clean solutions with love for systems and architecture.");
        System.out.println("🚀 Always learning. Always shipping.");
    }
}
```


<p align="center">
  <!-- Languages -->
  <img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white"/>
  <img src="https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white"/>

  <!-- Frameworks -->
  <img src="https://img.shields.io/badge/Spring%20Boot-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>

  <!-- Databases -->
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white"/>
  <img src="https://img.shields.io/badge/Cassandra-1287B1?style=for-the-badge&logo=apache-cassandra&logoColor=white"/>

  <!-- APIs -->
  <img src="https://img.shields.io/badge/REST-02569B?style=for-the-badge&logo=rest&logoColor=white"/>
  <img src="https://img.shields.io/badge/GraphQL-E10098?style=for-the-badge&logo=graphql&logoColor=white"/>

  <!-- DevOps & CI/CD -->
  <img src="https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitLab%20CI/CD-FC6D26?style=for-the-badge&logo=gitlab&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white"/>

  <!-- Containers & Cloud -->
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white"/>
  <img src="https://img.shields.io/badge/Cloud-AWS/GCP/Azure-232F3E?style=for-the-badge&logo=cloud&logoColor=white"/>
</p>


## 💡 О себе
- 🧠 **Анализирую**, **автоматизирую**, **систематизирую** процессы  
- 📞 Работаю с: **VoIP**, системами мониторинга, **Linux**-инфраструктурой  
- 🧬 Увлекаюсь: архитектурой **операционных систем**, низкоуровневым программированием  
- 📚 Читаю:
  - Техническую литературу
  - Психологию
  - Философию  
- 🎯 Хобби:
  - 🚴 Велоспорт
  - 🔫 Страйкбол
  - ✈️ Авиасимуляторы (Boeing 737NG flight simulator)

 
## 🎓 Образование и Курсы
- 🎓 **K.G. Razumovsky MSUTM**, Москва  
  *Бакалавриат* (090301 - Автоматизированные системы обработки информации и управления)

- 🧠 **Курсы и повышение квалификации**  
  **SkillFactory**, **Yandex Practicum**  
  Специализации:
  - System Analysis  
  - Full Stack Development  
  - Cisco Routing & Switching
  - Software architecture

 
## 📬 Контакты
- 📱 Telegram: [@tirexswa](https://t.me/tirexswa)  
- 📧 Email: [archibk32@yandex.ru](mailto:archibk32@yandex.ru)


My coding time 😤

<!--START_SECTION:waka-->

```rust
From: 18 November 2023 - To: 03 August 2025

Total Time: 85 hrs 53 mins

Java              40 hrs 18 mins  >>>>>>>>>>>>-------------   46.92 %
JavaScript        21 hrs 41 mins  >>>>>>-------------------   25.26 %
CSS               13 hrs 44 mins  >>>>---------------------   16.01 %
HTML              5 hrs 52 mins   >>-----------------------   06.85 %
HTTP Request      40 mins         -------------------------   00.79 %
Markdown          28 mins         -------------------------   00.55 %
TypeScript        25 mins         -------------------------   00.49 %
Java Properties   18 mins         -------------------------   00.37 %
PlantUML file     18 mins         -------------------------   00.36 %
```

<!--END_SECTION:waka-->
