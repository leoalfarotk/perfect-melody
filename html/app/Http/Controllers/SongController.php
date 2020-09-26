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
        $humming_file = $request->file('humming');
        $save_name = storage_path() . '/' . Str::random();

        $saved = Storage::put($save_name, $humming_file);

        if ($saved === false) {
            return APIResponse::error(500, 'Could not save the audio file');
        }

        $results = exec(config('app.python_script') . " $save_name");
        $results = json_decode($results);

        dd($results);
        unlink($save_name);

        return APIResponse::done($results);
    }
}
