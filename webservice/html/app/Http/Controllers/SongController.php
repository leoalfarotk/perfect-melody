<?php

namespace App\Http\Controllers;

use App\Http\Responses\APIResponse;
use Faker\Factory;
use Illuminate\Http\Request;

class SongController extends Controller
{
    public function __invoke(Request $request)
    {
        $faker = Factory::create();
        $response = [];

        for ($i = 0; $i < 10; ++$i) {
            $response[] =
                [
                    'name' => $faker->words(4, true),
                    'artist' => $faker->words(2, true),
                    'confidence' => $faker->biasedNumberBetween(0, 300),
                ];
        }

        usort($response, function ($first, $second) {
            if ($first['confidence'] === $second['confidence']) {
                return 0;
            }

            return ($first['confidence'] < $second['confidence']) ? -1 : 1;
        });

        return APIResponse::done($response);
    }
}
