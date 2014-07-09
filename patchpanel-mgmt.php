<?php

$page['patchpanels']['title'] = 'Patchpanels';

$page['patchpanels']['parent'] = 'index';
$tab['patchpanels']['default'] = 'View patchpanels';

$tabhandler['patchpanels']['default'] = 'patchpanel_overview';

$page['patchpanel']['parent'] = 'patchpanels';
$page['patchpanel']['bypass'] = 'patchpanel_id';
$page['patchpanel']['bypass_type'] = 'uint';
$page['patchpanel']['title'] = 'Patchpanel';
$tab['patchpanel']['default'] = 'Patchpanel info';
$tabhandler['patchpanel']['default'] = 'patchpanel_info';



function patchpanel_overview() 
{
	startPortlet ('Patchpanel Information');
	echo "<table class=cooltable align=center border=0 cellpadding=5 cellspacing=0> \n";
	echo "<tr><th>Name</th></tr>";
	$result = usePreparedSelectBlade ("SELECT Object.id, Object.name from Object where Object.objtype_id = 9;");
	$rows = $result->fetchAll (PDO::FETCH_ASSOC);
	$odd = FALSE;
	foreach ($rows as $row)
	{
		$tr_class = $odd ? 'row_odd' : 'row_even';
		echo "<tr class=$tr_class><td class=tdleft>";
		echo mkA ($row['name'], 'patchpanel',$row['id']);
		echo "</td></tr>\n";
		$odd = !$odd;
	}
	echo "</table>";
	finishPortlet();
}

function patchpanel_info($patchpanel_id) 
{
	startPortlet ('Patchpanel ');
	print $patchpanel_id;
	
	finishPortlet();
}
?>