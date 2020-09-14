<?php

namespace App\Http\Middleware;

use App\Http\Responses\APIResponse;
use Closure;
use Illuminate\Http\Request;

class AuthorizationToken
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        if ($request->hasHeader('X-Perfect-Melody-Token')) {
            if ($request->header('X-Perfect-Melody-Token') == config('app.authorization_token')) {
                return $next($request);
            }

            return APIResponse::error(2, 'Token not valid.', 401);
        }

        return APIResponse::error(1, 'Token not present.', 401);
    }
}
