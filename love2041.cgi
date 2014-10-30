#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use Date::Calc;
#use Array::Utils qw(:all);
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
$debug = 0;
$students_dir = "./students";

# if user is logged in
if(defined param("user") && defined param("pass") && verified(param("user"), param("pass")) && !defined param("logout")){
    %user_id = ();
    opendir(my $DIR, $students_dir);
    while(my $entry = readdir $DIR){
	next unless -d $students_dir . "/" . $entry;
	next if $entry eq "." or $entry eq "..";
	$user_id{$entry} = 0;
    }
    $i = 0;
    foreach my $user(sort keys %user_id){
	$user_id{$user} = $i++;
    }
    if(defined param("view_profile")){
	param("n", $user_id{param("view_profile")});
	print profile_screen();
    } elsif(defined param("find") && defined param("find_profile")){
	if(exists $user_id{param("find_profile")}){
    	    param("n", $user_id{param("find_profile")});
	    print profile_screen();
	} else {
	    print "User not found", home_screen();
	}
    } elsif(defined param("Match Me")){
	print match_screen();
    } else {
	print home_screen();
    }
} else {
    print login_screen();
}	

print page_trailer();
exit 0;	

sub verified {
    my $user = $_[0];
    my $pass = $_[1];
    if(-d "$students_dir/$user"){
	open F, "$students_dir/$user/profile.txt" or die "can not open$students_dir/$user/profile.txt: $!";
	while ($line = <F>){
	    if($line =~ /password:\s*$/){
		$realPass = <F>;
		$realPass =~ s/\s*//g;
		if($realPass eq $pass){
		    return 1;
		}
	    }
	}
    } 
    print "<div class=\"alert alert-danger\" role=\"alert\">Incorrect Username or Password</div>", "\n";
    return 0;
}

sub home_screen {
    if(defined param("page")){
  	if(defined param("next_page")){
	    $page = param("page") + 10;
	} elsif(defined param("prev_page")){
	    $page = param("page") - 10;
	}
    } else {
	$page = 0;
    }
    param("page", $page);
    my @users = ();
    opendir(my $DIR, $students_dir);
    while(my $entry = readdir $DIR){
	next unless -d $students_dir . "/" . $entry;
 	next if $entry eq "." or $entry eq "..";
	push @users, $entry;
    }
    @users = sort @users;
    @gallery = ();
    push @gallery, "<div align=center style=\"width:1350px; margin:100px auto\">";
    for my $n ($page..$page + 9){
    	my $prof_pic = $students_dir . "/" . @users[$n] . "/profile.jpg";
	push @gallery, "<div style=\"float:left; margin:5px\">\n";
#	push @gallery, image_button(-src=>$prof_pic, -name=>"view_profile", -value=>"@users[$n]", -border=>"1");
	push @gallery, img{-src=>$prof_pic, -class=>"img-thumbnail"}, "<br>";
	push @gallery, "<button type=\"submit\" name=\"view_profile\" value=@users[$n] class=\"btn btn-primary btn-sm\">@users[$n]</button>";
	push @gallery, "</div>\n";
    }
    push @gallery, "</div>";
    return  p, "\n",
    	    start_form(-method=>"GET"), "\n",
	    "<div class=\"container-fluid\" align=center>",
	    navigation(),
	    @gallery,
	    "<div align=center style=\"clear:both; padding-top:50px\">", "\n",
	    hidden("page"), "\n",
	    hidden("user"), "\n",
	    hidden("pass"), "\n",
	    "<button type=\"submit\" name=\"prev_page\" class=\"btn btn-primary\" align=left>Prev</btn>", "\n",
#	    submit("prev_page"), "\n".
	    "<button type=\"submit\" name=\"next_page\" class=\"btn btn-primary\" align=right>Next</btn>", "\n",
#	    submit("next_page"), "\n",
	    "</div>", "\n",
	    submit("logout"), "\n",
	    "</div>", "\n",
	    end_form, "\n",
	    p, "\n";
}

sub navigation {
    $user = param("user");
    return  "<nav class=\"navbar navbar-default\" role=\"navigation\">", "\n",
 	    "    <div>", "\n",
	    "        <table class=\"table\" align=center width=\"100%\">", "\n",
	    "            <tr valign=\"center\">", "\n",
	    "                <td width=\"33%\" align=\"right\"><span class=\"navbar-brand\">LOVE2041 <small><span class=\"glyphicon glyphicon-heart\"></span> Find yo bae.</small></span></td>", "\n",
	    "	         <td width=\"34%\" align=\"center\"><button type=\"submit\" name=\"Match Me\" value=\"Match Me\" class=\"btn btn-danger\">Find my Soulmate</button></td>", "\n",
	    "	         <td width=\"33%\" align=\"center\">", "\n",
	    "                    <form class=\"navbar-form navbar-left\" role=\"search\">", "\n",
	    "                        <div class=\"input-group\" align=right style=\"width:300px; margin-left:auto; padding-top:8px\">", "\n",
	    "                            <input type=\"text\" name=\"find_profile\" class=\"form-control\" placeholder=\"Search\">", "\n",
	    "                            <span class=\"input-group-btn\"><button type=\"submit\" name=\"find\" value=\"find\" class=\"btn btn-default\">Search</button></span>", "\n",
	    "                        </div>", "\n",
	    "                    </form>", "\n",
	    "                </td>", "\n",
	    "            </tr>", "\n",
            "        </table>", "\n",
	    "    </div>", "\n",
	    "</nav>", "\n";
}

sub match_screen {
    my $user = param("user");
    
    my %my_pref = ();
    my %my_info = ();

    my $student_loc = "$students_dir/$user";

    open F, "$student_loc/preferences.txt" or die "can not open $student_loc/preferences.txt: $!";
    while($line = <F>){
  	if($line =~ /gender:/){
	    $line = <F>;
	    chomp $line;
	    $line =~ s/^\s*//g;
	    push (@{$my_pref{"gender"}}, $line);
	} elsif($line =~ /age:/){
	    for(0..1){	#once for min then again for max
		$line = <F>; $line = <F>;
		chomp $line;
		$line =~ s/^\s*//g;
		push (@{$my_pref{"age"}}, $line);
	    }
	} elsif($line =~ /hair_colours:/){
	    $line = <F>;
	    while($line =~ /^\s+/){
		chomp $line;
		$line =~ s/^\s*//g; 
		push (@{$my_pref{"hair"}}, $line);
		$line = <F>;
	    }
	} elsif($line =~ /height:/){
	    for(0..1){
		$line = <F>; $line = <F>;
                chomp $line;
                $line =~ s/^\s*//g;
                push (@{$my_pref{"height"}}, $line);
	    }
	} elsif($line =~ /weight:/){
            for(0..1){
                $line = <F>; $line = <F>;
                chomp $line;
                $line =~ s/^\s*//g;
                push (@{$my_pref{"weight"}}, $line);
            }
        }
    }
    close F;

    open F, "$student_loc/profile.txt" or die "can not open $student_loc/profile.txt: $!";
    my $n;
    while($line = <F>){
  	chomp $line;
        if($line =~ /\s*([^ ]*):\s*$/){
            $n = $1;
        } else {
            $line =~ s/^\s*//g;
	    $line =~ s/\s*$//g;
            push(@{$my_info{$n}}, $line);
        }
    }
    close F;

    if(!defined @{$my_pref{"gender"}}){
	push @{$my_pref{"gender"}}, "any"; #assume no gender pref
    }
    if(!defined @{$my_pref{"age"}}){
	if($my_info{"birthdate"}[0] =~ /([0-9]{2})\/([0-9]{2})\/([0-9]{4})/){
            $b_day = $1 - 1;$b_month = $2 - 1;$b_year = $3 - 1;
        } elsif($my_info{"birthdate"}[0] =~ /([0-9]{4})\/([0-9]{2})\/([0-9]{2})/){
            $b_day = $3 - 1;$b_month = $2 - 1;$b_year = $1 - 1;
        }
        
	($day, $month, $year) = (localtime)[3..5];
        $year += 1900;

        my $age = $year - $b_year;
        $age-- unless sprintf("%02d%02d", $month, $day)
                   >= sprintf("%02d%02d", $b_month, $b_day); #birthday has not passed yet

        push @{$my_pref{"age"}}, ((($age/2) + 7), (($age - 7) * 2)); #scientifically proven for min/max age
    }
    if(!defined @{$my_pref{"hair"}}){
        push @{$my_pref{"hair"}}, "any"; #assume they dont care
    }
    if(!defined @{$my_pref{"height"}}){
        push @{$my_pref{"height"}}, "any";
    }
    if(!defined @{$my_pref{"weight"}}){
        push @{$my_pref{"weight"}}, "any";
    }

    %scores = ();
    my @users = ();
    opendir(my $DIR, $students_dir);
    while(my $entry = readdir $DIR){
        next unless -d $students_dir . "/" . $entry;
        next if $entry eq "." or $entry eq ".." or $entry eq $user;
        push @users, $entry;
    }

    %my_movies = ();
    foreach (@{$my_info{"favourite_movies"}}){
	$my_movies{$_}++;
    }
    %my_books = ();
    foreach (@{$my_info{"favourite_books"}}){
	$my_books{$_}++;
    }
    %my_tv = ();
    foreach (@{$my_info{"favourite_TV_shows"}}){
        $my_tv{$_}++;
    }
    %my_hobbies = ();
    foreach (@{$my_info{"favourite_hobbies"}}){
        $my_hobbies{$_}++;
    }
    %my_bands = ();
    foreach (@{$my_info{"favourite_bands"}}){
        $my_bands{$_}++;
    }
    %my_courses = ();
    foreach (@{$my_info{"courses"}}){
        $my_courses{$_}++;
    }	

    foreach $candidate (@users){
	$student_loc = "$students_dir/$candidate";
	%their_info = ();
	open F, "$student_loc/profile.txt" or die "can not open $student_loc/profile.txt: $!";
        my $c;
        while($line = <F>){
            if($line =~ /\s*([^ ]*):\s*$/){
	        $c = $1;
	    } else { 
	        $line =~ s/^\s*//g;
		$line =~ s/\s*$//g;
	        push(@{$their_info{$c}}, $line);
	    }
	}
	close F;

	if($their_info{"gender"}[0] ne $my_pref{"gender"}[0] && $my_pref{"gender"}[0] ne "any"){
	    $scores{$candidate} = 0;
	    next;
	}

	$age_score = 0;		#/20
	$hair_score = 0;	#/20
	$height_score = 0;	#/20
	$weight_score = 0;	#/20

	if($their_info{"birthdate"}[0] =~ /([0-9]{2})\/([0-9]{2})\/([0-9]{4})/){
	    $b_day = $1 - 1;$b_month = $2 - 1;$b_year = $3 -1;
	} elsif($their_info{"birthdate"}[0] =~ /([0-9]{4})\/([0-9]{2})\/([0-9]{2})/){
	    $b_day = $3 - 1;$b_month = $2 - 1;$b_year = $1 -1;
	}
		
	($day, $month, $year) = (localtime)[3..5];
	$year += 1900;

	my $age = $year - $b_year;
	$age-- unless sprintf("%02d%02d", $month, $day)
		   >= sprintf("%02d%02d", $b_month, $b_day); #birthday has not passed yet

	if($age >= $my_pref{"age"}[0] && $age <= $my_pref{"age"}[1]){
	    $age_score = 20;
	} elsif($age > $my_pref{"age"}[1]){
	    $age_score = max(0, 20 - ($age - $my_pref{"age"}[1])*3); #-3 points for each year above 
	} else {
	    $age_score = max(0, 20 - ($my_pref{"age"}[0] - $age)*3); #-3 points for each year below 
	}

	if($my_pref{"hair"}[0] eq "any"){
	    $hair_score = 20;
	} elsif(defined $their_info{"hair_colour"}[0]){
	    foreach $colour (@{$my_pref{"hair"}}){
	  	if($their_info{"hair_colour"}[0] eq $colour){
	            $hair_score = 20;
		}
	    }
	}

	if($my_pref{"height"}[0] eq "any"){
	    $height_score = 20;
	} else {
	    if(defined $their_info{"height"}[0]){
	 	$t_height = ($their_info{"height"}[0] =~ s/\D//g);
	 	$min_height = ($my_pref{"height"}[0] =~ s/\D//g);
		$max_height = ($my_pref{"height"}[1] =~ s/\D//g);
		if($t_height >= $min_height && $t_height <= $max_height){
		    $height_score = 10;
		} elsif($t_height > $max_height){
		    $height_score = max(0, 20 - ($t_height - $max_height)*100);
		    #-1 point for every .01m above max
		} else {
		    $height_score = max(0, 20 - ($min_height - $t_height)*100);
		    #-1 point for every .01m below min
		}
	    } 
	} #no height specified = 0 points

	if($my_pref{"weight"}[0] eq "any"){
            $weight_score = 20;
        } else {
            if(defined $their_info{"weight"}[0]){
                $t_weight = ($their_info{"weight"}[0] =~ s/\D//g);
                $min_weight = ($my_pref{"weight"}[0] =~ s/\D//g);
                $max_weight = ($my_pref{"weight"}[1] =~ s/\D//g);
                if($t_weight >= $min_weight && $t_weight <= $max_weight){
                    $weight_score = 10;
                } elsif($t_weight > $max_weight){
                    $weight_score = max(0, 20 - ($t_weight - $max_weight)*3);
                    #-3 points for every 1kg above max
                } else {
                    $weight_score = max(0, 20 - ($min_weight - $t_weight)*3);
                    #-3 point for every  1kg below min
                }
	    }
        } #no weight specified = 0 points

	$scores{$candidate} = ($age_score + $hair_score + $height_score + $weight_score);

	$common_score = 0;
	foreach (@{$their_info{"favourite_movies"}}){
	    if (defined $my_movies{$_}){
		$common_score += 3;
	    }
	}
	foreach (@{$their_info{"favourite_books"}}){
            if (defined $my_books{$_}){
                $common_score += 3;
            }
        }
        foreach (@{$their_info{"favourite_TV_shows"}}){
            if (defined $my_tv{$_}){
                $common_score += 3;
            }
        }
        foreach (@{$their_info{"favourite_bands"}}){
            if (defined $my_bands{$_}){
                $common_score += 3;
            }
        }
        foreach (@{$their_info{"favourite_hobbies"}}){
            if (defined $my_hobbies{$_}){
                $common_score += 5;
            }
        }
        foreach (@{$their_info{"courses"}}){
            if (defined $my_courses{$_}){
                $common_score += 1;
            }
        }
	if(defined($their_info{"degree"}[0]) && defined($my_info{"degree"}[0]) &&$their_info{"degree"}[0] eq $my_info{"degree"}[0]){ $common_score += 5;}

	$scores{$candidate} += $common_score;
    }

    foreach $candidate (keys %scores){
	if($scores{$candidate} < 70){
	    delete($scores{$candidate});
	}
    }

    @soulmates = sort {$scores{$b} <=> $scores{$a}} keys(%scores);
    @table = ();
    foreach(@soulmates){
	push @table, "<tr><td align=\"right\"><button type=\"submit\" name=\"view_profile\" value=\"$_\">$_</button></td><td align=\"left\">$scores{$_}</td></tr>", "\n";
    }

    return  p,
	start_form(-method=>"POST"), "\n",
	"<div class=\"container-fluid\" align=center>", "\n",
	navigation(),
	"<h1>", scalar @soulmates, " Matches Found</h1>", "\n",
	"<table class=\"table table-striped\">", "\n",
	"<col align=\"left\"><col align=\"right\">", "\n",
	"<tr><th style=\"text-align:right\">Username</th><th>Compatibility Score</th></tr>", "\n",
	@table,
	"</table>", "\n",
	"</div>", "\n",
	end_form(), "\n",
	hidden("user"), "\n",
	hidden("pass"), "\n",
	p, "\n";
}

sub login_screen {
    return  p, "\n",
	    start_form(-method=>"POST"), "\n",
	    "<div class=\"container\" align=center style=\"margin-top:25vh\">", "\n",
	    "<h1>LOVE2041<small><br>Find yo bae.</small></h1>", "\n",
	    "    <div style=\"width:500px; margin-top:50px\" align=center>", "\n",
	    "        <div>", "\n",
	    "            <div class=\"input-group input-group-lg\" style=\"margin-bottom:10px\">", "\n",
	    "                <span class=\"input-group-addon\"><span class=\"glyphicon glyphicon-user\"></span></span>", "\n",
	    "                <input type=\"text\" class=\"form-control\" placeholder=\"Username\" name=\"user\">", "\n",
	    "            </div>", "\n",
	    "            <div class=\"input-group input-group-lg\" style=\"margin-bottom:10px\">", "\n",
	    "                <span class=\"input-group-addon\"><span class=\"glyphicon glyphicon-lock\"></span></span>", "\n",
	    "                <input type=\"password\" class=\"form-control\" placeholder=\"Password\" name=\"pass\">", "\n",
	    "            </div>", "\n",
	    "        </div>", "\n",
	    "        <div>", "\n",
	    "            <button type=\"submit\" name=\"Login\" class=\"btn btn-success btn-lg\"><span class=\"glyphicon glyphicon-log-in\"></span></button>", "\n",
	    "        </div>", "\n",
	    "    </div>", "\n",
	    "</div>", "\n",
	    end_form, "\n",
	    hidden("user"),
	    hidden("pass"),
	    p, "\n";
}

sub profile_screen {
    my $n = param('n') || 0;
    my @students = glob("$students_dir/*");
    $n = min(max($n, 0), $#students);
    my $student_to_show  = $students[$n];
    my $profile_filename = "$student_to_show/profile.txt";
    open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
    %details = ();
    while($line = <$p>){
	if($line =~ /\s*([^ ]*):\s*$/){
 	    $n = $1;
	} else {
	    $line =~ s/^\s*//;
	    push(@{$details{$n}}, $line);
	}
    }
    $profile = "";
    foreach my $field(keys %details){
    	if($field =~ /^(name|email|password|courses)$/){
	    next;
	}
	$profile .= "$field\n";
	foreach $item (@{$details{$field}}){
	    $profile .= "$item";
	}
        $profile .= "\n";
    }
    close $p;
    $prof_pic_loc = "$student_to_show/profile.jpg";

    return  p, "\n",
	    start_form(-method=>"POST"), "\n",
	    "<div align=\"center\">", "\n",
	    img {src=>$prof_pic_loc, border=>"5"}, "\n",
	    pre($profile),"\n",
	    hidden('n', $n + 1),"\n",
	    submit('Return'),"\n",
	    "</div>",
	    hidden("user"),
	    hidden("pass"),
	    end_form, "\n",
	    p, "\n";
}

#
# HTML placed at bottom of every screen
#
sub page_header {
    return header,	
           start_html("-title"=>"LOVE2041", -bgcolor=>"#FEDCBA", -head => [ Link( { -rel => 'stylesheet', -type => 'text/css', -href => "https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css"}), ]);
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}
