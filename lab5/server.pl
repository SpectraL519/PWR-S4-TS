use HTTP::Daemon;
use HTTP::Status;
use IO::File;

my $daemon = HTTP::Daemon->new(
    LocalAddr => "localhost",
    LocalPort => 1234,
) || die;

print("Listening at ", $daemon->url, "\n");

while (my $connection = $daemon->accept) {
    while (my $request = $connection->get_request) {
        if (not $request->method eq "GET") {
            $connection->send_error(RC_FORBIDDEN);
            continue;
        }

        my $url = $request->uri->path;

        if ($url eq "/header") {
            # Respond with client headers.
            my $headers = $request->headers_as_string;
            my $response = HTTP::Response->new(200);

            $response->header("Content-Type" => "text/plain");
            $response->content($headers);
            $connection->send_response($response);
        } 
        else {
            $connection->send_file_response("./webpage" . $url);
        }
    }

    $connection->close;
    undef($connection);
}