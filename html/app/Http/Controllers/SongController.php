<?php

namespace App\Http\Controllers;

use App\Http\Responses\APIResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class SongController extends Controller
{
    public function __invoke(Request $request)
    {
        $save_name = $request->file('humming')->store('');
        $saved_file_path = storage_path() . '/app/' . $save_name;

        $results = exec(config('app.python_script') . " $saved_file_path");
        $results = json_decode($results);

        unlink($saved_file_path);

        $parsed_results = [];
        $counter = 0;

        foreach ($results as $key => $value) {
            if ($counter >= 10) {
                break;
            }

            $artist_name = explode(' - ', $key)[0];
            $song_name = explode('.', explode(' - ', $key)[1])[0];
            $confidence = $value;

            $parsed_results[] = [
                'name' => $song_name,
                'artist' => $artist_name,
                'confidence' => $confidence,
            ];

            ++$counter;
        }

        return APIResponse::done($parsed_results);
    }
}
