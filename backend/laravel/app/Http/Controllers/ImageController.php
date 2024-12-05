<?php

namespace App\Http\Controllers;

use App\Models\Image;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class ImageController extends Controller
{
    private $flaskApiUrl = 'http://localhost:5000/api';

    public function upload(Request $request)
    {
        $request->validate([
            'image' => 'required|image|max:10240',
            'category' => 'required|string'
        ]);

        $path = $request->file('image')->store('public/images');
        $url = Storage::url($path);

        // Send image to Flask service for feature extraction
        $response = Http::attach(
            'image', 
            file_get_contents(storage_path('app/' . $path)), 
            basename($path)
        )->post($this->flaskApiUrl . '/features');

        if (!$response->successful()) {
            return response()->json(['error' => 'Feature extraction failed'], 500);
        }

        $features = $response->json();

        $image = Image::create([
            'path' => $path,
            'url' => $url,
            'category' => $request->category,
            'features' => json_encode($features)
        ]);

        return response()->json($image);
    }

    public function search(Request $request)
    {
        $request->validate([
            'image' => 'required|image|max:10240',
            'use_relevance_feedback' => 'boolean'
        ]);

        $path = $request->file('image')->store('temp');

        // Send query image to Flask service
        $response = Http::attach(
            'query_image',
            file_get_contents(storage_path('app/' . $path)),
            basename($path)
        )->post($this->flaskApiUrl . '/search', [
            'use_relevance_feedback' => $request->use_relevance_feedback ?? false
        ]);

        Storage::delete($path);

        if (!$response->successful()) {
            return response()->json(['error' => 'Search failed'], 500);
        }

        return response()->json($response->json());
    }

    public function relevanceFeedback(Request $request)
    {
        $request->validate([
            'relevant_ids' => 'required|array',
            'irrelevant_ids' => 'required|array'
        ]);

        $response = Http::post($this->flaskApiUrl . '/relevance_feedback', [
            'relevant_ids' => $request->relevant_ids,
            'irrelevant_ids' => $request->irrelevant_ids
        ]);

        if (!$response->successful()) {
            return response()->json(['error' => 'Feedback processing failed'], 500);
        }

        return response()->json($response->json());
    }
}