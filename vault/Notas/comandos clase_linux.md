---
id: nota-28
tipo: nota
fecha_actualizacion: 2026-05-11T15:55:39.487339
---

# comandos clase_linux

**Categoría:** comandos
**Subcategoría:** Linux CLI Fundamentals
**Tags:** #linux, #bash, #filesystem, #permissions, #post-explotacion, #cli
**Origen:** comandos clase_linux.txt

## Resumen

Colección de comandos básicos y de uso forense/reconocimiento en sistemas Linux. Incluye navegación del sistema de archivos, gestión de permisos, búsqueda de archivos, manipulación de texto y control de procesos. Algunos comandos como find, history y uname tienen utilidad directa en fases de post-explotación y reconocimiento local.

## Contenido

pwd
ls
.
..
../..
cd
vi
mkdir
ls -a 
whoami
chmod 777
chmod 000
chmod 661
mkdir -p
touch
rm
rm -rf
cd ~
rm -r
cp
grep
grep -r
mv
cat
head -n
tail -n
find / -name {} 2>/dev/null
history
uname -a
history -c
history -pkalkali
find
find . name ¨*.txt¨
find / name "*.tmp"
find / name "*.tmp"
find .perm /u+x | head -10
file
du -h | sort -rt
kill %
echo " lo que sea">
echo " lo que sea">>
mkdir x ; mkdir x
$PATH

## Entidades relacionadas

[[find]]
[[grep]]
[[vi]]
[[Comando-118]]
[[Comando-119]]
[[Comando-120]]
[[Comando-121]]
[[Comando-122]]
[[Comando-123]]
[[Comando-124]]
[[Comando-125]]
[[Comando-126]]
[[Comando-127]]
[[Comando-128]]
[[Comando-129]]
[[Comando-130]]
[[Comando-131]]
[[Comando-132]]
