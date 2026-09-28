---
id: nota-32
tipo: nota
fecha_actualizacion: 2026-05-11T15:57:39.623895
---

# Fibonacci_comando

**Categoría:** herramienta
**Subcategoría:** Bash scripting - Fibonacci sequence generator
**Tags:** #bash, #scripting, #fibonacci, #validacion-entrada, #automatizacion
**Origen:** Fibonacci_comando.txt

## Resumen

Script de Bash que genera la secuencia de Fibonacci hasta el n-ésimo término. Incluye validación de parámetros de entrada, verificando que el argumento sea un número entero positivo antes de ejecutar el cálculo iterativo. No tiene relación directa con ciberseguridad, pero puede ser útil como plantilla de scripting con validación robusta de entradas.

## Contenido

#!/bin/bash


# Comprobación de parámetro

if [ -z "$1" ]; then

  echo "Uso: $0 <numero>"

  exit 1

fi


if ! [[ "$1" =~ ^[0-9]+$ ]]; then

  echo "Error: el parámetro debe ser un número entero positivo."

  exit 1

fi


n=$1


if [ "$n" -eq 0 ]; then

  exit 0

fi


a=0

b=1


for (( i=0; i<n; i++ )); do

  echo $a

  temp=$((a + b))

  a=$b

  b=$temp

done

## Entidades relacionadas

[[Comando-178]]
