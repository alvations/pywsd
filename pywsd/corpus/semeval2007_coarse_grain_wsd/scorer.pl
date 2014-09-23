#!/usr/bin/perl

# answer key file
$key_file = "dataset21.test.key";

if (scalar(@ARGV) == 0)
{
	print "Semeval coarse-grained WSD scorer\n";
	print "=======================\n";
	print "Usage: scorer.pl <answer_file> [options]\n";
	print "\nwhere the options are:\n\n";
	print "-w\tprint wrong sense assignments\n";
	print "-m\tprint missed sense assignments\n";
	print "-d\tprint an evaluation document by document\n";
	print "-x\texclude one-cluster words\n";
	print "-a\tprint answer by answer\n\n";
	exit;
}

# system answer file
$filename = $ARGV[0];

# options
for ($k = 0; $k < scalar(@ARGV); $k++)
{
	$options{$1} = 1 if ($ARGV[$k] =~ /^-(\w)/);
}

# exclude one-cluster words?
if ($options{'x'})
{
	open IN, "sense_clusters-21.senses" or die "Unable to open the sense clustering file: 'sense_clusters-21.senses'";
	
	while(<IN>)
	{
		if (/^([^%]+)%(\d):/)
		{
			($lemma, $pos) = ($1, $2);
			$pos = '3' if ($pos eq '5');
			$cluster_no{lc $lemma.$pos}++;
		}
	}
	
	close IN;
}

# load the solution
open IN, $key_file or die "Unable to open the answer key: '$key_file'";

%total_by_doc = %id2keys = ();

while(<IN>)
{
	chomp;
	
	if (/^(d\d+) (d\d+\.s\d+\.t\d+) ([^!]+)/)
	{
		($doc, $id, $keys) = ($1, $2, $3);
		
		if ($options{'x'})
		{
			($lemma, $pos) = $keys =~ /^([^%]+)%(\d):/;
			$pos = '3' if ($pos eq '5');
			
			next if ($cluster_no{lc $lemma.$pos} < 2);
		}
		
		$id2keys{$id} = {};
		$keys{$id} = $keys;
		
		for $key (split / /, $keys)
		{
			$id2keys{$id}->{lc $key} = 1;
		}
		$total_by_doc{$doc}++;
	}
}

close IN;

for $id (keys %id2keys) { $id_assessment{$id} = 'n'; }
	
print "$filename\n---\n";

open IN, $filename or die "Unable to open the system answer file: '$filename'";

%given_by_doc = %correct_by_doc = %given = %correct = ();

# load the answer file
while(<IN>)
{
	chomp;

	if (/^(d\d+) (d\d+\.s\d+\.t\d+) ([^ ]+)/)
	{
		($doc, $id, $key) = ($1, $2, $3);

		if ($options{'x'})
		{
			($lemma, $pos) = $key =~ /^([^%]+)%(\d):/;
			$pos = '3' if ($pos eq '5');
			
			next if ($cluster_no{lc $lemma.$pos} < 2);
		}

		if (!exists $correct_by_doc{$doc}) { $correct_by_doc{$doc} = {}; }
		if (!exists $given_by_doc{$doc}) { $given_by_doc{$doc} = {}; }

		if (exists $id2keys{$id})
		{
			if (exists $id2keys{$id}->{lc $key})
			{
				$correct_by_doc{$doc}->{$id} = 1;
				$correct{$id} = 1;

				# mark the assignment as 'correct'
				$id_assessment{$id} = 'c';
				
				if ($options{'a'})
				{
					print "score for \"$id\": 1.000\n";
					print "  key   = $keys{$id}\n";
					print "  guess = $key\n\n";
				}
			}
			else
			{
				# delete previous (possibly correct) assignments with the same id:
				# only the last sense assignment matters
				delete $correct_by_doc{$doc}->{$id};
				delete $correct{$id};
				
				# mark the assignment as 'wrong'
				$id_assessment{$id} = 'w';

				if ($options{'a'})
				{
                                	print "score for \"$id\": 0.000\n";
                                	print "  key   = $keys{$id}\n";
                                	print "  guess = $key\n\n";
				}
			}
		
			$given_by_doc{$doc}->{$id} = $given{$id} = 1;
		}
		else
		{
			print "** $id does not exist\n";
		}
	}
}

close IN;

# list missing and/or wrong sense assignments
for $id (sort keys %id_assessment)
{
	if (($options{'m'})&&($id_assessment{$id} eq 'n')) { print "Missing: $id\n"; }
	elsif (($options{'w'})&&($id_assessment{$id} eq 'w')) { print "Wrong: $id\n"; }
}

# evaluation by document
if ($options{'d'})
{
	# for each document
	for $doc (sort keys %total_by_doc)
	{
		$correct = scalar(keys %{$correct_by_doc{$doc}});
		$given = scalar(keys %{$given_by_doc{$doc}});
		$total = $total_by_doc{$doc};
		
		$a = $given/$total;
		$p = $given > 0 ? $correct/$given : 'NaN';
		$r = $correct/$total;
		$f1 = $p+$r > 0 ? (2*$p*$r)/($p+$r) : 'NaN';

		printf "$doc:\tA = %.3f ($given / $total), P = %.5f ($correct / $given), R = %.5f ($correct / $total), F1 = %.5f\n", $a, $p, $r, $f1;
	}
}

# overall results
$correct = scalar(keys %correct);
$given = scalar(keys %given);
$total = scalar(keys %id2keys);

$a = $given/$total;
$p = $given > 0 ? $correct/$given : 'NaN';
$r = $correct/$total;
$f1 = $p+$r > 0 ? (2*$p*$r)/($p+$r) : 'NaN';

printf "\nTotal:\tA = %.3f ($given / $total), P = %.5f ($correct / $given), R = %.5f ($correct / $total), F1 = %.5f\n\n", $a, $p, $r, $f1;
print "Legenda: A = attempted, P = precision, R = recall, F1 = F1 measure\n";
