<?php

namespace App\Http\Responses;

use Illuminate\Http\JsonResponse;

class APIResponse
{
    /**
     * @param null $body
     * @param int  $http_code
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public static function done($body = null, $http_code = 200)
    {
        $response = ['status_code' => 0];

        if ($body and ! is_array($body)) {
            $body = $body->toArray();
        }

        $response['body'] = $body !== null ? $body : [];

        return new JsonResponse($response, $http_code);
    }

    /**
     * @param     $message
     * @param int $http_code
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public static function message($message, $http_code = 200)
    {
        $response = [
            'status_code' => 0,
            'message' => $message,
        ];

        return new JsonResponse($response, $http_code);
    }

    /**
     * @param        $status
     * @param        $message
     * @param int    $http_code
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public static function error($status, $message, $http_code = 422)
    {
        $response = [
            'status_code' => $status,
            'message' => $message,
        ];

        return new JsonResponse($response, $http_code);
    }
}
