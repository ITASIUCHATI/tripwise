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
        const normalizedEmail = email
            .trim()
            .toLowerCase();

        const existingUser =
            await this.prisma.user.findUnique({
                where: {
                    email: normalizedEmail,
                },
            });

        if (existingUser) {
            throw new UnauthorizedException(
                'Email already exists',
            );
        }

        const hashedPassword =
            await bcrypt.hash(password, 10);

        const user =
            await this.prisma.user.create({
                data: {
                    email: normalizedEmail,
                    password: hashedPassword,
                },
            });

        return this.authResponse(user);
    }

    async login(
        email: string,
        password: string,
    ) {
        const normalizedEmail = email
            .trim()
            .toLowerCase();

        let user =
            await this.prisma.user.findUnique({
                where: {
                    email: normalizedEmail,
                },
            });

        if (
            normalizedEmail ===
                'demo@tripwise.app' &&
            password === 'TripWise@123' &&
            !user
        ) {
            const hashedPassword =
                await bcrypt.hash(
                    password,
                    10,
                );

            user =
                await this.prisma.user.create({
                    data: {
                        email: normalizedEmail,
                        password: hashedPassword,
                    },
                });

            await this.prisma.trip.updateMany({
                where: {
                    userId: null,
                },
                data: {
                    userId: user.id,
                },
            });
        }

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

        return this.authResponse(user);
    }

    private authResponse(user: {
        id: number;
        email: string;
    }) {
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
