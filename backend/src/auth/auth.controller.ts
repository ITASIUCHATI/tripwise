import {
    Body,
    Controller,
    Post,
} from '@nestjs/common';
import {
    IsEmail,
    IsString,
    Matches,
    MinLength,
} from 'class-validator';

import { AuthService } from './auth.service';

class AuthDto {
    @IsEmail({}, { message: 'Please enter a valid email address.' })
    @Matches(/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/, {
        message: 'Please enter a valid email address with a domain.'
    })
    email!: string;

    @IsString()
    @MinLength(6)
    password!: string;
}

@Controller('auth')
export class AuthController {
    constructor(
        private readonly authService: AuthService,
    ) {}

    @Post('register')
    register(@Body() dto: AuthDto) {
        return this.authService.register(
            dto.email,
            dto.password,
        );
    }

    @Post('login')
    login(@Body() dto: AuthDto) {
        return this.authService.login(
            dto.email,
            dto.password,
        );
    }
}