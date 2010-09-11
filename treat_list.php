<?php

//$sansd = explode( "\r\n", file_get_contents( 'Sans_image.txt' ) );
//$sansx = explode( "\r\n", file_get_contents( 'Sans_OCR.txt' ) );
//$sansdavecc = explode( "\n", file_get_contents( 'Avec_dossier_C.txt' ) );
//$arks = explode( "\r\n", file_get_contents( 'wipedia liste.csv.arks_20100112163856' ) );
$resolutions = file_get_contents( 'resolution.txt' );
$pagelists = file_get_contents( 'pagelists.txt' );

$line = 0;

function searchArk( $matches ) {
	
	global $line, $resolutions, $pagelists;
	
	$ok        = $matches[1];
	$taux      = $matches[2];
	$ordre     = $matches[3];
	$etat      = $matches[4];
	$cote      = $matches[5];
	$auteur    = $matches[6];
	$titre     = $matches[7];
	$page0     = $matches[8];
	$pages     = $matches[9];
	$titdjvu   = $matches[10];
	$titcour   = $matches[11];
	$ark       = $matches[12];
	$idbnf     = $matches[13];
	$folderx   = $matches[14];
	$folderdca = $matches[15];
	$bonauteur = $matches[16];
	
	/* Remplacement des apostrophes dans les titre djvu
	$titdjvu = preg_replace( '/’/u', '\'', $titdjvu );
	*/
	
	/* Création de titres courts corrects
	$titcour = '';
	
	$auteur_clean = preg_replace( array('/à/u','/[éèêë]/u','/[îï]/u','/[öô]/u','/[ùûü]/u','/[œ]/u'), array('a','e','i','o','u','oe'), $auteur );
	$auteur_clean = preg_replace( array('/À/u','/[ÉÈÊË]/u','/[ÎÏ]/u','/[ÖÔ]/u','/[ÙÛÜ]/u','/[Œ]/u'), array('a','E','I','O','U','OE'), $auteur_clean );
	$auteur1 = explode( ' ', $auteur_clean );
	$titcour .= preg_replace( '/[^a-zA-Z0-9]/u', '', $auteur1[0] );
	
	$titre_clean = preg_replace( array('/à/u','/[éèêë]/u','/[îï]/u','/[öô]/u','/[ùûü]/u','/[œ]/u'), array('a','e','i','o','u','oe'), $titre );
	$titre_clean = preg_replace( array('/à/u','/[éèêë]/u','/[îï]/u','/[öô]/u','/[ùûü]/u','/[œ]/u'), array('a','e','i','o','u','oe'), $titre_clean );
	$titre1 = explode( ' ', $titre_clean );
	for( $i=0; $i<count($titre1) && strlen($titcour)<40 && $i<4; $i++ ) $titcour .= preg_replace( '/[^a-zA-Z0-9]/u', '', $titre1[$i] );
	*/
	
	/* Modification des titres djvu */
	//$titdjvu = preg_replace( '/(.*), (.*) - (.*).djvu/u', '$1 - $3.djvu', $titdjvu );
	
	/* Correction des ARKs *
	$ark = '[http://gallica.bnf.fr/'.$arks[$line].' '.$arks[$line].']';
	
	/* Ajout des infos sur la présence des dossiers X *
	$folderx = 'X';
	if( in_array( $ordre, $sansx ) ) $folderx = '';
	
	/* Ajout des infos sur la présence des dossiers D, C, A *
	$folderdca = 'D';
	if( in_array( $ordre, $sansd ) ) {
		
		if( in_array( $ordre, $sansdavecc ) ) $folderdca = 'C';
		else $folderdca = '';
	}
	
	/* Fin */
	
	$line = $line + 1;
	
	preg_match( "/".$idbnf." (\d*)\n/", $resolutions, $res );
	$resol = $res[1];
	
	preg_match( "/".$idbnf." (.*)\n/", $pagelists, $res );
	$pagelist = $res[1];
	
	//ordre|titrecourt|titredjvu|ark|titre|auteur|resolution|pagelist
	//return $idbnf."|".$titcour."|".$titdjvu."|".$ark."|".$titre."|".$auteur."|".$resol."|".$pagelist."|".$bonauteur."\n";
	//return $titdjvu."\n";
	if( $folderx == 'X' ) return '';
	else return $idbnf."\n";
	/*return "|-
|".$ok."
|".$taux."
|".$ordre."
|".$etat."
|".$cote."
|".$auteur."
|".$titre."
|".$page0."
|".$pages."
|".$titdjvu."
|".$titcour."
|".$ark."
|".$idbnf."
|".$folderx."
|".$folderdca."
";*/
}

$ipagews = file_get_contents( 'lists_ws_in.txt' );

/*$opagews = preg_replace_callback( "/\|\-
\|(.*)
\|(.*)
\|(\d*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(\d*)
\|(\d*)
\|(.*)
\|(.*)
\|.* (.*)\]
\|(.*)
\|(.*)
\|(.*)
\|(.*)
/", "searchArk", $ipagews );*/







$ipagews = preg_replace( "/\r\n/", "\n", $ipagews );

$opagews = preg_replace_callback( "/\|\-
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|(.*)
\|.* (.*)\]
\|(.*)
\|(.*)
\|(.*)
\|(.*)
/", "searchArk", $ipagews );


file_put_contents( 'lists_ws_out.txt', $opagews );

echo "$line lignes traitées\n";

