# NebulaTech – Manual del Desarrollador: Mejores Prácticas en Ingeniería AI/ML y MLOps

---

## Introducción

En NebulaTech, nuestros desarrolladores construyen sistemas inteligentes que transforman la manera en que operan las empresas.  
Este manual sirve como base para un desarrollo de IA consistente y de alta calidad en todos los equipos.  
Nuestra cultura de ingeniería enfatiza colaboración, reproducibilidad e innovación responsable.

**Principios clave:**

- Claridad sobre ingenio  
- Reproducibilidad sobre velocidad  
- Automatización sobre repetición manual  
- Aprendizaje compartido sobre silos

---

## Estándares de Código

Usamos principalmente Python 3.10+ para desarrollo de IA.  
El código debe seguir las convenciones **PEP8** y ser formateado con **black** y **flake8**.  
Se requieren anotaciones de tipo en todo el código de producción.

**Estructura del repositorio:**

project_name/
├── data/
├── notebooks/
├── src/
│ ├── preprocessing/
│ ├── models/
│ └── utils/
├── tests/
└── README.md


- Usar **pytest** para testing, con al menos un test por módulo.  
- Los mensajes de commit deben ser descriptivos, por ejemplo:  
  `feat(model): agregar clasificador de sentimiento v2`.

---

## Pipelines de Datos

Los datos son la base de todo proyecto de IA. Para asegurar consistencia:

- Versionar todos los datasets usando **DVC** o **LakeFS**  
- Documentar el lineage: rastrear fuentes, transformaciones y propietarios de los datos  
- Validar datasets con **Great Expectations**  
- Usar esquemas para detectar drift o campos faltantes temprano

**Flujo típico:**

1. Ingesta de datos crudos desde fuentes seguras (S3, GCP, Azure)  
2. Transformación y limpieza en Spark o Pandas  
3. Registro en feature store (**Feast**)  
4. Salida versionada almacenada en `/processed/`

---

## Desarrollo de Modelos

Cada modelo debe ser reproducible y explicable.  
Usar **MLflow** para tracking de experimentos y registrar cada modelo entrenado con metadatos:

- Versión del dataset  
- Hash del commit de código  
- Hiperparámetros  
- Métricas de evaluación

**Métricas según tarea:**

- Clasificación: Precisión, Recall, F1-score, ROC-AUC  
- Regresión: RMSE, MAE, R²  
- NLP: BLEU, ROUGE

Se prefieren scripts de entrenamiento modulares sobre notebooks para pipelines de producción.  
Prototipos de notebooks solo en `/notebooks/experimental/`.

---

## Workflows de MLOps

MLOps asegura que los sistemas de ML sean estables, escalables y mantenibles.  
Workflow de NebulaTech:

1. **Integración Continua (CI)** — Linting, testing y validación de modelos en GitHub Actions  
2. **Entrega Continua (CD)** — Despliegue automatizado a staging usando **Docker** y **Kubernetes**  
3. **Registro de Modelos** — Modelos versionados en **MLflow Registry**, promovidos automáticamente tras validación  
4. **Monitoreo** — Seguimiento de drift de datos, latencia y rendimiento de predicciones con **Prometheus + Grafana**

Toda la infraestructura se gestiona con **Terraform**; no se permiten cambios manuales en clusters de producción.

---

## Infraestructura

Todos los proyectos corren en entornos cloud-native con orquestación de contenedores:

- Compute: AWS (EKS), GCP (GKE), Azure (AKS)  
- Almacenamiento: S3 / GCS / Azure Blob  
- Despliegue: Charts de Helm en Kubernetes  
- Logging: ELK Stack (Elasticsearch, Logstash, Kibana)

Se deben usar las imágenes internas de NebulaTech:  
`nebulatech/python-ml:base` y `nebulatech/mlflow:server`.

---

## Seguridad y Cumplimiento

La seguridad se integra en cada etapa:

- Usar variables de entorno para credenciales (nunca hardcodear)  
- Encriptar todos los datos en reposo y en tránsito (AES-256, TLS 1.2+)  
- Aplicar acceso de mínimo privilegio mediante roles IAM  
- Revisar librerías de terceros trimestralmente para vulnerabilidades  
- Todos los outputs de modelos deben pasar la auditoría de IA ética de NebulaTech para sesgo, equidad e interpretabilidad

---

## Mejores Prácticas

1. Automatizar todo: CI/CD, testing, validación de datos  
2. Documentar mientras se programa: docstrings y README  
3. Revisar peer todos los pull requests antes de mergear  
4. Contenerizar experimentos para reproducibilidad  
5. Registrar parámetros y métricas consistentemente  
6. Preferir servicios gestionados sobre autoalojados, salvo justificación  
7. Guardar secretos en **Vault** o gestores de secretos en la nube

---

## Errores Comunes

- Entrenar con datos obsoletos o no versionados  
- Faltas de comparaciones baseline  
- Ignorar desequilibrio de clases  
- Subir notebooks directamente a producción  
- Falta de documentación o propiedad poco clara  
- Ignorar alertas de drift de modelos

Cada fallo es una oportunidad de aprendizaje — registrar retrospectivas en **Notion**.

---

## Recursos

**Herramientas internas:**

- NebulaFlow (pipeline interno de MLOps)  
- MLflow Registry  
- Data Portal

**Referencias externas:**

- Google MLOps Whitepaper  
- AWS Well-Architected ML Lens  
- DeepLearning.AI MLOps Specialization

Para preguntas: contactar a `mlops@nebulatech.ai` o revisar el canal **#mlops-support** en Slack.

