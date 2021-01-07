#!/usr/bin/perl
use strict;
use Switch;
#use Carp::Assert;

my $file = $ARGV[$#ARGV-1];
my $userfile = $ARGV[$#ARGV];
if ($ARGV[$#ARGV] eq "-h" || "$#ARGV" eq "-1") {
    print "\n\nThe command line syntax for running this script is\n\n";
    print "perl blif2verilog.pl <blif file> <output file>\n\n"; 
    print "Here blif file is the name of your blif file which you want to parse with the .blif extension\n\n";
    print "And the output file is the output base file name\n\n";
    print "For example, if you say\n\n";
    print "perl script abc.blif xyz\n\n";
    print "Then the script would parse abc.blif and generate xyz.v\n"; 
}
else {
    my $blifString;
    {
        print "Parsing $file\n";
        print "Please wait...\n";
        $userfile =~ s/\..*//;
        open (OUTFILE, ">$userfile.v") || die "Cannot create .v :$!";
        open(INFILE, "<$file")|| die "Cannot open blif: $!";
        local $/ = undef ;
        $blifString=<INFILE>;
        close(INFILE);
    }
    my @buffer=();
    #$blifString=~ s/(\[)|(\])/_/gm; #get rid of comments and extra lines
    #$blifString=~ s/([^\s])\[(\d*)\]/$1($2)/gm;
    $blifString=~s/([^\w])\[(\d*)\]/$1wire$2/gm;
    $blifString=~ s/(\\\n)//gm;
    $blifString=~ s/[ ]+/ /gm;
    my @blifBlocks=split(/\./,$blifString);
    
    my $ending_value = scalar(@blifBlocks) ;
    my %primaryVariableHash=();
    my %variableHash=();
    my @inputList;
    my @outputList;
    my @nodeList;
    my @regList;
    my @initialList;
    # @Array returns a scalar in this context
    for(my $counter=0 ; $counter < $ending_value ; $counter++)
    {
        my @currentLines=split(/\n/,$blifBlocks[$counter]);
        my @currentNames=split(/\s+/,$currentLines[0]); #split the first line of the block
        my $numNames = scalar(@currentNames) ;
        switch ($currentNames[0]) {
            case "latch" {
                shift(@currentNames);
                my $input = shift(@currentNames);
                my $output = shift(@currentNames);
                push @regList,$output ;
                my $temp = join(" ",@currentNames);
                $temp =~ m/^((fe|re|ah|al|as)\s+([^\s]+))?(\s*(0|1))?/i;
                my $type = $2;
                my $control = $3;
                #assert( $control !~ /NIL/i);
                my $init_val = $5;
                if(not $init_val eq ""){
                    push @initialList, "$output = $init_val;";
                }
                if(not $type eq "" ){
                    push @buffer, "always ";                
                    switch ($type) {
                        case "fe" {push @buffer, "@(negedge $control)\n\t$output<=$input;\n\n"}
                        case "re" {push @buffer, "@(posedge $control)\n\t$output<=$input;\n\n"}
                        case "ah" {push @buffer, "@($control)\n\tif($control) $output<=$input;\n\n"}
                        case "al" {push @buffer, "@($control)\n\tif(!$control) $output<=$input;\n\n"}
                        case "as" {push @buffer, "@($input)\n\t$output<=$input;\n\n"}
                        else      { print( "Latch [$output] type [$type] not found");exit(-1) }
                    }
                }else{
                    push @buffer, "always @($input)\n\t$output<=$input;\n\n";
                }                
            }
            case "inputs" {
                shift(@currentNames);
                foreach my $nodeName (@currentNames){
                    #$primaryVariableHash{$nodeName}='pin';
                    if (not $nodeName eq "") {
                        push @inputList,$nodeName ;
                    }
                }            
            }
            case "outputs" {
                shift(@currentNames);
                foreach my $nodeName (@currentNames){
                    $primaryVariableHash{$nodeName}='output';
                    if (not $nodeName eq "") {
                        push @outputList,$nodeName ;
                    }
                }            
            }   
            case "names"{
                if(not $primaryVariableHash{$currentNames[$numNames-1]}){
                    if(not $variableHash{$currentNames[$numNames-1]}){
                        push @nodeList,$currentNames[$numNames-1] ;
                    }
                }
                shift(@currentLines);
                
                foreach my $line (@currentLines){
                    my @eqn=();
                    for(my $NameCounter=1 ; $NameCounter < $numNames-1 ; $NameCounter++){
                        $line=~s/\s1//;
                        if($line=~m/^1/){ #found a 1
                            $line=~s/^1(.*)/$1/;
                            push @eqn," $currentNames[$NameCounter] " ;
                        }
                        elsif ($line=~m/^0/){ #found a 1
                            $line=~s/^0(.*)/$1/;
                            push @eqn," (~ $currentNames[$NameCounter]) " ;
                        }
                        else{
                            $line =~ s/-//;
                        }
                    }
                    $line ='(' . join(" & ",@eqn) . ')';
                }
                if(scalar(@currentLines) eq 0){ #prob set eq to logic high
                    push @buffer, "assign $currentNames[$numNames-1] =((~ ". $inputList[0].") & ". $inputList[0].");\n";
                }else{            
                    push @buffer, "assign $currentNames[$numNames-1] =", join(" | ",@currentLines) , ";\n";
                }
            }
        }
    }
    #print OUTFILE "SUBDESIGN 'testing'\n(\n";
    my @IO;
    push(@IO, @inputList);
    push(@IO, @outputList);
    my $c = 1;#if not(++$c%10)
    #print map( +("$_\n","\n" if not(++$c%10)) , @IO);
    print ;
    print OUTFILE
        "module $userfile (\n\t",
        join (", ", map( (++$c%10)?"$_":"\n\t$_" , @IO)),");\n\n",
        "input ",join(", ",@inputList),";\n\n",
        "output ",join(", ",@outputList),";\n\n",
        "wire ",join(", ",@nodeList), ";\n\n";
    print OUTFILE
        "reg ",join(", ",@regList), ";\n\n" if scalar @regList;
    print OUTFILE
        "initial\nbegin\n\t",join("\n\t",@initialList), "\nend\n\n" if scalar @initialList;
    print OUTFILE
        "@buffer\n",
        "\nendmodule\n\n";
    close(OUTFILE);
    print "Done!\n"
     
}