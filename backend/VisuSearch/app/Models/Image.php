<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Image extends Model
{
    protected $fillable = [
        'path',
        'url',
        'category',
        'features'
    ];

    protected $casts = [
        'features' => 'array'
    ];
}