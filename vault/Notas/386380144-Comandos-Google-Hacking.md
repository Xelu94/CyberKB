---
id: nota-25
tipo: nota
fecha_actualizacion: 2026-05-11T15:54:08.971112
---

# 386380144-Comandos-Google-Hacking

**Categoría:** reconocimiento
**Subcategoría:** Google Dorks / OSINT pasivo
**Tags:** #google-dorks, #osint, #sql-injection, #directory-listing, #carding, #guatemala, #information-disclosure, #php-vulnerabilities, #index-of
**Origen:** 386380144-Comandos-Google-Hacking.txt

## Resumen

El documento contiene un listado de Google Dorks orientados a reconocimiento pasivo sobre dominios guatemaltecos (.gt, .gob.gt, .edu.gt), incluyendo búsqueda de directorios expuestos, archivos sensibles, errores de base de datos y configuraciones vulnerables. También incluye dorks específicos para carding (robo de tarjetas) apuntando a tiendas online con parámetros PHP vulnerables. Finalmente lista URLs con parámetros GET potencialmente vulnerables a SQL Injection para uso con herramientas de dumping.

## Contenido

LISTADO DE EJERCICIOS
-----------------------------------------
site:gt index of /| curriculum
site:gob.gt index of * "Last modified | 2015"
site:edu.gt index of * "Last modified | 2015"
site:gt "sendmail.conf"
site:gt "Statistics for"
site:gt index of user.php
site:gt "Bienvenido a phpMyAdmin"
site:gob.gt ".sql"
site:gt index of DB.php
site:gt "Microsoft OLE DB Provider for ODBC"
site:gt "Warning: mysql_fetch_row():"
site:gt /_vti_pvt/
site:gt "Warning: mysql_query()"
site:gt index of user.xml
site:gt "Warning: mysql_fetch_array():"
site:gt "Warning: readdir():"
site:gt index of DB.php
site:gt "/wamp/"
site:gt "/sqlitemanager/"
site:gt "What are the requirements to run Joomla!"
site:gt "vti_encoding:SR"
site:gt "vti_backlinkinfo"
site:gt "vti_cachedhastheme"
site:gt "vti_modifiedby"
site:gt "utf8-nl vti_author"
site:edu.gt Index of@_vti_cnf/
site:gt "Content-Type: text/html\n "
site:gt "Server.MapPath("db.mdb")"
site:gt Index of /images/files "2010"
site:gob.gt Index of /home

site:usac.edu.gt Index of   (auditar una web en busca NAT TRANSVERSAL)

site:gt Index of test.txt
site:segeplan.gob.gt Index of /descargas | Name privado
site:gob.gt listado de personal | informatica
Index of /admin/
Index of /.htaccess
Index of /HTMLEditor
Index of /site/
Index of /Parent Directory
index of /com_user/
Index of / .ftpquota
Index of /adodb

-----------------------------------------
site:gt password filetype:txt | xml | xls
site:gt login filetype:txt | xml | xls
site:gt user filetype:txt | xml | xls
site:gt usuario filetype:txt | xml | xls
site:gt user filetype:txt intext:pass
site:gt contrase�a intext:pass
site:gt password intext:contrase�a
site:gt usuario intext:null
site:gt password intext:null
site:gt login intext:null intext:error
Localizacion Navegaci�n Anonyma
site:gt inurl:"gt:8000"
site:gt inurl:"gt:8080"
site:gt inurl:"gt:8088"
site:gt inurl:"gt:80"
site:gt inurl:"gt:8043"


site:gt webcontrol
site:gt filetype:xls "tel"
site:gt filetype:xls | doc | txt "tel"
site:gt filetype:xls "correo"
site:gt filetype:xls "Direccion Personal"
site:gt intext:"zabbix"
site:gt intext:"xampp/index.php"
site:gt IIS intext:asp
site:gt IIS intext:pass
site:gt IIS intext:access
site:gt SQL intext:"user name" -google -adobe
site:gt SELECT intext:"user List"
site:gt MYSQL intext:"error"
site:gt PHP intext:"query"
site:gt webmail intext:Username

-----------------------------
Carding Dorks 2015 Fresh (Utilizado en el robo de tarjetas)
-----------------------------
inurl:".php?cat="+intext:"Paypal"+site:UK
inurl:".php?cat="+intext:"/Buy Now/"+site:.net
inurl:".php?cid="+intext:"online+betting"
inurl:".php?id=" intext:"View cart"
inurl:".php?id=" intext:"Buy Now"
inurl:".php?id=" intext:"add to cart"
inurl:".php?id=" intext:"shopping"
inurl:".php?id=" intext:"boutique"
inurl:".php?id=" intext:"/store/"
inurl:".php?id=" intext:"/shop/"
inurl:".php?id=" intext:"toys"
inurl:".php?cid="
inurl:".php?cid=" intext:"shopping"
inurl:".php?cid=" intext:"add to cart"
inurl:".php?cid=" intext:"Buy Now"
inurl:".php?cid=" intext:"View cart"
inurl:".php?cid=" intext:"boutique
inurl:".php?cid=" intext:"/store/"
inurl:".php?cid=" intext:"/shop/"
inurl:".php?cid=" intext:"Toys"
inurl:".php?cat="
inurl:".php?cat=" intext:"shopping"
inurl:".php?cat=" intext:"add to cart"
inurl:".php?cat=" intext:"Buy Now"
inurl:".php?cat=" intext:"View cart"
inurl:".php?cat=" intext:"boutique
" inurl:".php?cat=" intext:"/store/"
inurl:".php?cat=" intext:"/shop/"
inurl:".php?cat=" intext:"Toys"
inurl:".php?catid="
inurl:".php?catid=" intext:"View cart"
inurl:".php?catid=" intext:"Buy Now"
inurl:".php?catid=" intext:"add to cart"
inurl:".php?catid=" intext:"shopping"
inurl:".php?catid=" intext:"boutique"
inurl:".php?catid=" intext:"/store/"
inurl:".php?catid=" intext:"/shop/"
inurl:".php?catid=" intext:"Toys"
inurl:".php?categoryid="
inurl:".php?categoryid=" intext:"View cart"
inurl:".php?categoryid=" intext:"Buy Now"
inurl:".php?categoryid=" intext:"add to cart"
inurl:".php?categoryid=" intext:"shopping"
inurl:".php?categoryid=" intext:"boutique"
inurl:".php?categoryid=" intext:"/store/"
inurl:".php?categoryid=" intext:"/shop/"
inurl:".php?categoryid=" intext:"Toys"
inurl:".php?pid="
inurl:".php?pid=" intext:"shopping"
inurl:".php?pid=" intext:"add to cart"
inurl:".php?pid=" intext:"Buy Now"
inurl:".php?pid=" intext:"View cart"
inurl:".php?pid=" intext:"boutique"



------------------------------------------------------
Esta seccion es para usar la herramienta de DUMPEO de su Cdrom de software

SQL VULNERABLE WEBSITES 2015
#########################################
Updated: 2015/07/01
#########################################
http://www.mygoodact.com/collectiondetailperson.php?id=212
http://www.medix.com.hr/aboutbook.php?id=33
http://vacationet.com/resort.php?id=2
http://www.orascomci.com/index.php?id=home
http://www.orascomci.com/index.php?id=talentprogram
http://www.bible-history.com/subcat.php?id=22
http://www.oiwsba.com/oiwsba/memberinfo.php?id=54
http://www.ci.bremerton.wa.us/display.php?id=221
http://www.pangeaday.org/filmDetail.php?id=74
http://www.vst4free.com/free_vst.php?id=187
http://www.cideko.com/pro_con.php?id=3
http://www.aradergalleries.com/catgallery.php?id=2
http://www.catholiccemeterieschicago.org/locations.php?id=11
http://www.orillia.com/index.php?id=22
http://www.medix.com.hr/aboutbook.php?id=30
http://hebron.com/english/gallery.php?id=170
http://www.carkitinc.com/carkit2.php?id=12
http://www.heavymetal.com/index.php?id=1520
http://www.sherrihill.com/content.php?id=registration
http://www.hebron.com/english/article.php?id=282
http://www.nickhawkexplicit.com/gallery.php?id=77
http://www.suagacollection.com/photo-gallery.php?id=1
http://www.daphne-emu.com/site3/faq_entry.php?id=59
http://overcomingapartheid.msu.edu/sidebar.php?id=5
http://www.myvegancookbook.com/recipes/recipe.php?id=16
http://orascomci.com/index.php?id=careers
http://www.thekenkirchoffteam.com/local_detail.php?id=166338
http://www.heavymetal.com/index.php?id=1946
http://www.bia2.com/video/player.php?id=17
http://www.bia2.com/video/player.php?id=37


Must Check :   Latest SQL Shopping injections 2015




http://jokusoftware.cz/file.php?id=icqj
http://www.nichegardens.com/catalog/item.php?id=1911
http://pokemon.supercheats.com/team.php?id=4059
http://www.uselitewine.com/index.php?id=1
http://www.ellafitzgerald.com/viewheadline.php?id=3418
http://www.bvfonts.com/fonts/details.php?id=45
http://mathman.dreamhosters.com/MathMan/Organization.php?id=7
http://www.vf-venieri.com/prodotto.php?id=2
http://www.teenmodeling.tv/join.php?id=5
http://www.magicwings.com/index.php?id=140
http://www.cochraneventilation.com/articledetails.php?id=9
http://remewing.118696.com/article.php?id=115
http://www.ladirectmodels.com/talent.php?id=829
http://www.sherylblais.com/index.php?id=5
http://www.southernpowerlifting.com/form.php?id=5
http://www.carkitinc.com/carkit2.php?id=5
http://cathedralhillpress.com/book.php?id=
http://gazetaonline.globo.com/noticias/radios/litoral/index.php?
id=/fale_conosco/faleconosco.php
http://tf2mods.net/mod.php?id=20
http://www.bia2.com/video/player.php?id=13
http://www.bvfonts.com/fonts/details.php?id=76
http://www.bitaraf.com/showlink.php?id=1244923
http://www.carbodydesign.com/goto.php?id=27
http://www.type-o-tones.com/fonts.php?id=29
http://www.killfromtheheart.com/bands.php?id=7
http://www.orascomci.com/index.php?id=aboutus
http://www.bmepainolympics2.com/comments/showmore.php?id=358
http://www.malcolmx.com/about/viewheadline.php?id=546
http://www.kaza-deluxe.com/category.php?id=45
http://bostonhigashi.org/about.php?id=1
http://www.simplytobago.com/gallery.php?id=47
http://www.interplay.com/games/support.php?id=42
http://www.mircscripts.org/ramblings.php?id=151
http://www.facingthegiants.com/news.php?id=2
http://www.nypdangels.com/cop/cop.php?id=90
http://www.vf-venieri.com/prodotto.php?id=3
http://www.pixheaven.net/galerie_us.php?id=22
http://www.ever.be/c_page.php?id=277
http://www.irishsanghatrust.ie/news.php?id=33
http://ditto3d.com/gallery.php?id=7
http://www.goodingproductions.com/shop.php?id=6
http://cathedralhillpress.com/book.php?id=1
http://www.romanianwriters.ro/s.php?id=1
http://www.benayoun.com/projet.php?id=16
http://www.karnaticlabrecords.com/cart.php?id=88
http://countryfest.ca/page.php?id=72
http://www.ath-elite.com.au/trainers.php?id=25
http://tjff.com/film-info.php?id=1471
http://www.rupri.org/dataresearchviewer.php?id=6
http://www.snowdonia-society.org.uk/index2.php?id=5
http://www.sfu.ac.at/english/index.php?id=66
http://www.raahauges.com/view-news.php?id=8
http://www.clanwilliam.info/index.php?id=1
http://www.cjsf.ca/pguide/grid/description.php?ID=38
http://www.kitefestpasirgudang.com/Content.php?id=2
http://www.kyygames.com/games.php?id=2
http://www.sciencedomain.org/page.php?id=general-guideline-for-authors
http://www.simplytobago.co.uk/gallery.php?id=47
http://www.backstagecommerce.ca/services.php?id=4
http://en.swfplay.net/game.php?id=104
http://www.imaginenative.org/program.php?id=91
http://www.jelco.ca/en/product_detail.php?id=2
http://www.bitaraf.com/showlink.php?id=1689155
http://www.sarilocker.com/advice/qa.php?id=1167
http://lm.inlinkz.com/ar.php?id=69722
http://www.gamedogped.com/details.php?id=47469
http://www.bvfonts.com/fonts/details.php?id=79
http://www.orascomci.com/index.php?id=media
http://www.twitney.co.uk/theme.php?id=7
http://www.atavistic.com/albums.php?id=8
http://www.drumheadmag.com/web/education.php?id=4
http://www.sisterstates.com/statetaxforms.php?id=43
http://house.legis.state.ak.us/rep.php?id=leu
http://www.everyway-medical.com/products.php?id=2
http://www.konfor.com.tr/Product.php?id=
http://www.ameliaearhart.com/viewheadline.php?id=2950
http://www.kjworks.com.tw/productdetail.php?id=1
http://www.pixheaven.net/photo_us.php?nom=110913_5877-78
http://www.pixheaven.net/galerie_us.php?id=16
http://www.pixheaven.net/galerie_us.php?id=10
http://tjff.com/film-info.php?id=100
http://www.sciencedomain.org/page.php?id=reviewers-editors
http://learnzone.org.uk/courses/course.php?id=1
http://www.tidytowns.ie/interior.php?id=2
http://encycl.anthropology.ru/article.php?id=1
http://www.cobranet.org/about.php?id=1
http://www.trnres.com/ebookcontents.php?id=93
http://www.goldencards.com/send1.php?id=65
http://www.reklamaru.com/content.php?id=269
http://www.prworldwidelive.com/index.php?id=188
http://www.polkatheatre.com/event.php?id=6
http://www.firstgulf.com/search-details.php?id=59
http://www.urldominator.com/ro.php?id=540
http://www.colinst.com/brief.php?id=61
http://www.kidswithfoodallergies.org/resourcespre.php?id=99
http://cjsf.ca/pguide/grid/description.php?ID=116
http://www.creationcare.org/blank.php?id=39
http://www.melbournefineart.com.au/gallery.php?id=18
http://www.orillia.com/index.php?id=23
http://www.lift.org/staffdetails.php?id=36
http://www.imaginenative.org/program.php?id=99
http://www.sciencedomain.org/journal-home.php?id=9
http://www.jfuinsurance.com/insurance/index.php?id=1137
http://www.thornbridgebrewery.com/beers.php?id=2
http://www.coldexrents.com/price_list.php?id=9


## Entidades relacionadas

[[SQLMap]]
[[Google Dorks]]
[[phpMyAdmin]]
[[XAMPP]]
[[Zabbix]]
[[Comando-86]]
[[Comando-87]]
[[Comando-88]]
[[Comando-89]]
[[Comando-90]]
[[Comando-91]]
[[Comando-92]]
[[Comando-93]]
[[Comando-94]]
[[Comando-95]]
