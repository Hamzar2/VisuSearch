<?php

use App\Http\Controllers\ImageController;
use Illuminate\Support\Facades\Route;

Route::post('/images/upload', [ImageController::class, 'upload']);
Route::post('/images/search', [ImageController::class, 'search']);
Route::post('/images/feedback', [ImageController::class, 'relevanceFeedback']);