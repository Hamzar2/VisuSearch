<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Image extends Model
{
    protected $fillable = [
        'path',
        'url',
        'category',
        'features',
        'hash'
    ];

    protected $casts = [
        'features' => 'array'
    ];

    protected $attributes = [
        'hash' => '',
    ];
}