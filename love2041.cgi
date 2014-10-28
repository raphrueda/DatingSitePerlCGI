#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
$debug = 1;
$students_dir = "./students";

# if user is logged in
if(defined param("user") && defined param("pass") && verified(param("user"), param("pass"))){
	if(defined param("view_profile")){
		%user_id = ();
		opendir(my $DIR, $students_dir);
		while(my $entry = readdir $DIR){
                	next unless -d $students_dir . "/" . $entry;
	                next if $entry eq "." or $entry eq "..";
	                $user_id{$entry} = 0;
        	}
		$i = 0;
		foreach my $user(sort keys %user_id){
			$user_id{$user} = $i;
			$i++;
		}
		param("n", $user_id{param("view_profile")});
		print profile_screen();
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
	print "Incorrect Username and/or Password";
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
	for my $n ($page..$page + 9){
		my $prof_pic = $students_dir . "/" . @users[$n] . "/profile.jpg";
		push @gallery, "<div style=\"float:left; margin:5px\">\n";
		push @gallery, img {src=>$prof_pic, border=>"1"}, "\n <br> \n";
		push @gallery, submit("view_profile", "@users[$n]");
		push @gallery, "</div>\n";
	}
	return  p, "\n",
		start_form(-method=>"GET"), "\n",
		"<div align=center style=\"width:1330px; margin:100px auto\">",
		@gallery,
		"</div>",
		"<div align=center style=\"clear:both; padding-top:50px\">",
		hidden("page"),
		hidden("user"),
		hidden("pass"),
		submit("prev_page"),
		submit("next_page"),
		"</div>",
		end_form,
		p, "\n";
}

sub login_screen {
	return  p, "\n",
		start_form(-method=>"POST"), "\n",
		textfield("user", "username"), "\n",
		p, "\n",
		password_field("pass", "password"), "\n",
		p, "\n",
		submit("Login"), "\n",
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
   		start_html("-title"=>"LOVE2041", -bgcolor=>"#FEDCBA"),
 		center(h2(i("LOVE2041"))), "\n";
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
