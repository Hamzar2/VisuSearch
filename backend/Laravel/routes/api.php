<?php

use App\Http\Controllers\ImageController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
Route::post('/images/upload', [ImageController::class, 'upload']);
Route::post('/images/search', [ImageController::class, 'search']);
Route::post('/images/feedback', [ImageController::class, 'relevanceFeedback']);
Route::post('/images/feedbackSearch', [ImageController::class,'feedbackSearch']);