# Airline-Full-Data-Analysis
import streamlit as st
import pandas as pd
import plotly.express as px
import re


✈️ Airline Fare Dashboard
Description

This dashboard provides an interactive visualization of airline fares, flight durations, and routes. Users can filter by airline, source/destination city, travel class, and currency. The dashboard displays key metrics, charts, and a heatmap of average prices per route.

Input Data

CSV files containing flight information

Key columns: Airline, Source City, Destination City, Class, Price, Duration, Days Left

Features

KPIs: Total Flights, Average Price, Average Duration, Cheapest & Most Expensive Flights

Charts:

Average Price by Airline

Average Price by Source-Destination Route

Price vs. Days Left

Flight Duration vs. Price

Heatmap showing average price per route

Data Model

Tabular data with flight info

Numeric columns cleaned and normalized

Aggregations calculated dynamically for visualizations

How to Run
streamlit run appairline.py


¡Claro! Aquí tienes una versión corta del README en español:

---

# ✈️ Dashboard de Tarifas Aéreas

## Descripción

Este dashboard proporciona una visualización interactiva de tarifas aéreas, duración de vuelos y rutas. Los usuarios pueden filtrar por aerolínea, ciudad de origen/destino, clase de viaje y moneda. El dashboard muestra métricas clave, gráficos y un mapa de calor con los precios promedio por ruta.

## Datos de Entrada

* Archivos CSV con información de vuelos
* Columnas clave: Aerolínea, Ciudad de Origen, Ciudad de Destino, Clase, Precio, Duración, Días Restantes

## Funcionalidades

* KPIs: Total de Vuelos, Precio Promedio, Duración Promedio, Vuelo Más Barato y Más Caro
* Gráficos:

  * Precio Promedio por Aerolínea
  * Precio Promedio por Ruta Origen-Destino
  * Precio vs. Días Restantes
  * Duración del Vuelo vs Precio
* Mapa de calor que muestra el precio promedio por ruta

## Modelo de Datos

* Datos tabulares con información de vuelos
* Columnas numéricas limpias y normalizadas
* Agregaciones calculadas dinámicamente para las visualizaciones

## Cómo Ejecutar

```bash
streamlit run appairline.py
```

---

Si quieres, puedo también redactar **una versión muy breve tipo “presentación”** para usar en GitHub que sea aún más resumida y clara para otros usuarios. ¿Quieres que haga eso?
