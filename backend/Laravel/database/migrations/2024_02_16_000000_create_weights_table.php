<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        if(schema::hasTable("weights")){
            Schema::create("weights", function (Blueprint $table)  {
                // $table->bigIncrements("id");
                $table->id("imageId");
                $table->json("weights");	
    
            });

        }
    }

    public function down()
    {
        Schema::dropIfExists("weights");
    }
};