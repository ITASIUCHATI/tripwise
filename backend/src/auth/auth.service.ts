import {
    Injectable,
    UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcryptjs';

import { PrismaService } from '../prisma.service';

@Injectable()
export class AuthService {
    constructor(
        private readonly prisma: PrismaService,
        private readonly jwt: JwtService,
    ) {}

    async register(
        email: string,
        password: string,
    ) {
        const existingUser = await this.prisma.user.findUnique({
            where: {
                email,
            },
        });

        if (existingUser) {
            throw new UnauthorizedException(
                'Email already exists',
            );
        }

        const hashedPassword = await bcrypt.hash(
            password,
            10,
        );

        const user = await this.prisma.user.create({
            data: {
                email,
                password: hashedPassword,
            },
        });

        return {
            token: this.jwt.sign({
                sub: user.id,
                email: user.email,
            }),
            user: {
                id: user.id,
                email: user.email,
            },
        };
    }

    async login(
        email: string,
        password: string,
    ) {
        const user = await this.prisma.user.findUnique({
            where: {
                email,
            },
        });

        if (
            !user ||
            !(await bcrypt.compare(
                password,
                user.password,
            ))
        ) {
            throw new UnauthorizedException(
                'Invalid credentials',
            );
        }

        return {
            token: this.jwt.sign({
                sub: user.id,
                email: user.email,
            }),
            user: {
                id: user.id,
                email: user.email,
            },
        };
    }
}